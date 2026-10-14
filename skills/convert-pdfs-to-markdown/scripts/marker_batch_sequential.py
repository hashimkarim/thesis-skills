#!/usr/bin/env python3
"""Run full Marker conversions sequentially while reusing loaded models.

This helper is executed inside the Marker uv environment by ``convert.py``.
It deliberately does not use multiprocessing: one converter runs at a time,
but the expensive model bundle is reused for a bounded number of documents.
"""

from __future__ import annotations

import argparse
import gc
import json
import tempfile
import time
import traceback
from pathlib import Path
from output_utils import publish_output

import torch
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
from marker.output import save_output


def convert_one(
    pdf: Path,
    dest_md: Path,
    models: dict,
    batch_size: int,
    minimum_memory: bool,
    disable_ocr: bool,
    force_ocr: bool,
    marker_package: str,
) -> tuple[bool, int, float]:
    """Convert one document with an already-loaded Marker model bundle."""
    options: dict[str, object] = {
        "output_format": "markdown",
        "disable_multiprocessing": True,
        "disable_tqdm": True,
        "layout_batch_size": batch_size,
        "detection_batch_size": batch_size,
        "recognition_batch_size": batch_size,
        "equation_batch_size": batch_size,
    }
    if minimum_memory:
        options["ocr_error_batch_size"] = batch_size
        options["table_rec_batch_size"] = batch_size
    if disable_ocr:
        options["disable_ocr"] = True
    if force_ocr:
        options["force_ocr"] = True

    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="marker-pdf-") as tmp:
        options["output_dir"] = tmp
        config_parser = ConfigParser(options)
        converter_cls = config_parser.get_converter_cls()
        converter = converter_cls(
            config=config_parser.generate_config_dict(),
            artifact_dict=models,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )
        rendered = converter(str(pdf))
        output_folder = config_parser.get_output_folder(str(pdf))
        save_output(rendered, output_folder, config_parser.get_base_filename(str(pdf)))
        markdown_files = sorted(Path(tmp).rglob("*.md"))
        if not markdown_files:
            raise RuntimeError("Marker produced no Markdown")
        assets = publish_output(markdown_files[0], dest_md, pdf, {
            "marker_package": marker_package, "batch_size": batch_size,
            "minimum_memory": minimum_memory, "disable_ocr": disable_ocr,
            "force_ocr": force_ocr,
        })
        del rendered
        del converter

    elapsed = time.monotonic() - started
    return True, assets, elapsed


def load_plan(path: Path) -> list[tuple[Path, Path]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("plan must be a JSON list")
    plan: list[tuple[Path, Path]] = []
    for item in raw:
        pdf = Path(item["pdf"]).resolve()
        # Preserve the final path component so publication can reject symlinks.
        dest_md = Path(item["dest_md"]).absolute()
        if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
            raise FileNotFoundError(f"invalid source PDF: {pdf}")
        plan.append((pdf, dest_md))
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--marker-package", required=True)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--minimum-memory", action="store_true")
    parser.add_argument("--disable-ocr", action="store_true")
    parser.add_argument("--force-ocr", action="store_true")
    parser.add_argument(
        "--reload-models-every",
        type=int,
        default=10,
        help="reload models after this many documents (default: 10)",
    )
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    if args.reload_models_every < 1:
        parser.error("--reload-models-every must be at least 1")
    if args.disable_ocr and args.force_ocr:
        parser.error("--disable-ocr cannot be combined with --force-ocr")

    plan = load_plan(args.plan)
    failed = False
    models = None
    for index, (pdf, dest_md) in enumerate(plan, start=1):
        if models is None or (index - 1) % args.reload_models_every == 0:
            if models is not None:
                del models
                gc.collect()
                torch.cuda.empty_cache()
            print(
                f"models: loading bundle for documents {index}--"
                f"{min(index + args.reload_models_every - 1, len(plan))}",
                flush=True,
            )
            models = create_model_dict()

        print(f"convert [{index}/{len(plan)}]: {pdf}", flush=True)
        try:
            _, assets, elapsed = convert_one(
                pdf,
                dest_md,
                models,
                args.batch_size,
                args.minimum_memory,
                args.disable_ocr,
                args.force_ocr,
                args.marker_package,
            )
            print(
                f"ok: {pdf} -> {dest_md} ({assets} assets, {elapsed:.1f}s)",
                flush=True,
            )
        except torch.OutOfMemoryError as error:
            if args.minimum_memory:
                failed = True
                print(f"failed: {pdf}: {error}", flush=True)
                traceback.print_exc()
            else:
                # Keep the complete Marker pipeline, but reduce the two large
                # default CUDA batches as well as the explicitly configured
                # batches to one. Retrying only after a demonstrated OOM
                # preserves the proven full-quality profile for normal PDFs.
                error.__traceback__ = None
                gc.collect()
                torch.cuda.empty_cache()
                print(
                    f"oom: {pdf}; retrying once with minimum-memory batches",
                    flush=True,
                )
                try:
                    _, assets, elapsed = convert_one(
                        pdf,
                        dest_md,
                        models,
                        1,
                        True,
                        args.disable_ocr,
                        args.force_ocr,
                        args.marker_package,
                    )
                    print(
                        f"ok-minimum-memory: {pdf} -> {dest_md} "
                        f"({assets} assets, {elapsed:.1f}s)",
                        flush=True,
                    )
                except Exception as retry_error:
                    failed = True
                    print(f"failed: {pdf}: {retry_error}", flush=True)
                    traceback.print_exc()
        except Exception as error:
            failed = True
            print(f"failed: {pdf}: {error}", flush=True)
            traceback.print_exc()
        finally:
            gc.collect()
            torch.cuda.empty_cache()

    if models is not None:
        del models
    gc.collect()
    torch.cuda.empty_cache()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
