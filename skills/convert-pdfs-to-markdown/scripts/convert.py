#!/usr/bin/env python3
"""Convert PDF files or directories to Markdown sequentially with Marker."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from output_utils import publish_output


# Marker 1.10.1 is deliberately pinned. Its native PyTorch/CUDA pipeline exposes
# every resource control used by this skill. Marker 2.x changed those controls
# and delegates its balanced VLM mode to a separate inference server, so
# silently resolving "marker-pdf" to latest would make conversions
# non-reproducible and can require Docker GPU setup.
DEFAULT_MARKER_PACKAGE = "marker-pdf==1.10.1"
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}
CONSERVATIVE_BATCH_OPTIONS = (
    "layout",
    "detection",
    "recognition",
    "equation",
)
HIGH_THROUGHPUT_BATCH_OPTIONS = ("ocr_error", "table_rec")
PERSISTENT_HELPER = Path(__file__).with_name("marker_batch_sequential.py")


def collect_pdfs(inputs: list[Path]) -> list[tuple[Path, Path]]:
    """Return (PDF, relative output path) pairs."""
    found: list[tuple[Path, Path]] = []
    for item in inputs:
        source = item.expanduser().resolve()
        if source.is_file() and source.suffix.lower() == ".pdf":
            found.append((source, Path(source.name)))
            continue
        if source.is_dir():
            for base, dirnames, filenames in os.walk(source):
                dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
                base_path = Path(base)
                for filename in filenames:
                    pdf = base_path / filename
                    if pdf.suffix.lower() == ".pdf":
                        found.append((pdf, pdf.relative_to(source)))
            continue
        raise FileNotFoundError(f"Not a PDF file or directory: {item}")
    unique: dict[Path, tuple[Path, Path]] = {}
    outputs: dict[str, Path] = {}
    for pdf, relative in sorted(found, key=lambda pair: str(pair[0])):
        if pdf in unique:
            continue
        key = relative.with_suffix(".md").as_posix().casefold()
        if key in outputs:
            raise ValueError(f"output collision: {outputs[key]} and {pdf}; use a common input root or separate outputs")
        outputs[key] = pdf
        unique[pdf] = (pdf, relative)
    artifacts = []
    for pdf, relative in unique.values():
        md = relative.with_suffix(".md")
        for target in (md, md.with_suffix(".source.json"), md.parent / f"{md.stem}_assets"):
            artifacts.append((tuple(part.casefold() for part in target.parts), pdf))
    artifacts.sort()
    for (previous, first), (current, second) in zip(artifacts, artifacts[1:]):
        if current[:len(previous)] == previous:
            raise ValueError(f"output paths overlap: {first} and {second}; use separate outputs")
    return list(unique.values())


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").lower() in {"1", "true", "yes"}


def uvx_command(marker_package: str, executable: str, *args: str) -> list[str]:
    return ["uvx", "--from", marker_package, executable, *args]


def cuda_probe(marker_package: str) -> tuple[dict[str, object] | None, str]:
    """Inspect CUDA from the exact environment that will execute Marker."""
    code = (
        "import json, torch; "
        "ok=torch.cuda.is_available(); "
        "print(json.dumps({'available':ok,'torch':torch.__version__,"
        "'device':torch.cuda.get_device_name(0) if ok else None,"
        "'memory_gib':round(torch.cuda.get_device_properties(0).total_memory/2**30,2) "
        "if ok else None}))"
    )
    result = subprocess.run(
        uvx_command(marker_package, "python", "-c", code),
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        return None, detail
    try:
        return json.loads(result.stdout.strip().splitlines()[-1]), ""
    except (IndexError, json.JSONDecodeError) as error:
        return None, f"could not parse CUDA probe: {error}"


def marker_command(
    pdf: Path,
    output: Path,
    marker_package: str,
    batch_size: int,
    minimum_memory: bool,
    disable_ocr: bool,
    force_ocr: bool,
) -> list[str]:
    command = uvx_command(
        marker_package,
        "marker_single",
        str(pdf),
        "--output_dir",
        str(output),
        "--output_format",
        "markdown",
        "--disable_multiprocessing",
        "--disable_tqdm",
    )
    # This is the full Marker pipeline in both profiles. Batch sizes change
    # throughput and peak VRAM, not which recognition stages run. The default
    # constrains the four heavier/shared stages and leaves OCR-error/table-recognition at the
    # pinned release's CUDA default of 14. --minimum-memory constrains all six.
    for option in CONSERVATIVE_BATCH_OPTIONS:
        command.extend((f"--{option}_batch_size", str(batch_size)))
    if minimum_memory:
        for option in HIGH_THROUGHPUT_BATCH_OPTIONS:
            command.extend((f"--{option}_batch_size", str(batch_size)))
    if disable_ocr:
        command.append("--disable_ocr")
    if force_ocr:
        command.append("--force_ocr")
    return command


def convert(
    pdf: Path,
    dest_md: Path,
    force: bool,
    marker_package: str,
    batch_size: int,
    minimum_memory: bool,
    disable_ocr: bool,
    force_ocr: bool,
) -> bool:
    if dest_md.exists() and not force:
        print(f"skip: {dest_md} (use --force to replace)", flush=True)
        return True
    with tempfile.TemporaryDirectory(prefix="marker-pdf-") as tmp:
        tmp_path = Path(tmp)
        env = os.environ.copy()
        env.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
        print(f"convert: {pdf}", flush=True)
        started = time.monotonic()
        result = subprocess.run(
            marker_command(
                pdf,
                tmp_path,
                marker_package,
                batch_size,
                minimum_memory,
                disable_ocr,
                force_ocr,
            ),
            env=env,
        )
        if result.returncode:
            print(f"failed: {pdf}", file=sys.stderr, flush=True)
            return False
        markdown = sorted(tmp_path.rglob("*.md"))
        if not markdown:
            print(
                f"failed: Marker produced no Markdown for {pdf}",
                file=sys.stderr,
                flush=True,
            )
            return False
        try:
            assets = publish_output(markdown[0], dest_md, pdf, {
                "marker_package": marker_package, "batch_size": batch_size,
                "minimum_memory": minimum_memory, "disable_ocr": disable_ocr,
                "force_ocr": force_ocr,
            })
        except (OSError, ValueError) as error:
            print(f"failed: {pdf}: {error}", file=sys.stderr, flush=True)
            return False
        elapsed = time.monotonic() - started
        print(
            f"ok: {pdf} -> {dest_md} ({assets} assets, {elapsed:.1f}s)",
            flush=True,
        )
        return True


def convert_persistent(
    pairs: list[tuple[Path, Path]],
    output_dir: Path,
    force: bool,
    marker_package: str,
    batch_size: int,
    minimum_memory: bool,
    disable_ocr: bool,
    force_ocr: bool,
    reload_models_every: int,
) -> bool:
    """Convert pending documents sequentially in one model-host process."""
    plan: list[dict[str, str]] = []
    for pdf, relative in pairs:
        dest_md = output_dir / relative.with_suffix(".md")
        if dest_md.exists() and not force:
            print(f"skip: {dest_md} (use --force to replace)", flush=True)
            continue
        plan.append({"pdf": str(pdf), "dest_md": str(dest_md)})

    if not plan:
        return True
    if not PERSISTENT_HELPER.is_file():
        print(f"failed: missing helper {PERSISTENT_HELPER}", file=sys.stderr)
        return False

    with tempfile.TemporaryDirectory(prefix="marker-plan-") as temporary:
        plan_file = Path(temporary) / "plan.json"
        plan_file.write_text(json.dumps(plan), encoding="utf-8")
        command = uvx_command(
            marker_package,
            "python",
            str(PERSISTENT_HELPER),
            "--plan",
            str(plan_file),
            "--marker-package",
            marker_package,
            "--batch-size",
            str(batch_size),
            "--reload-models-every",
            str(reload_models_every),
        )
        if minimum_memory:
            command.append("--minimum-memory")
        if disable_ocr:
            command.append("--disable-ocr")
        if force_ocr:
            command.append("--force-ocr")
        env = os.environ.copy()
        env.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
        return subprocess.run(command, env=env).returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--marker-package",
        default=os.environ.get("MARKER_PACKAGE", DEFAULT_MARKER_PACKAGE),
        help=f"uv package specifier (default: {DEFAULT_MARKER_PACKAGE})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help=(
            "batch size for layout, detection, recognition, and equation "
            "stages (default: 1)"
        ),
    )
    parser.add_argument(
        "--minimum-memory",
        action="store_true",
        help=(
            "also force OCR-error and table-recognition batches to "
            "--batch-size; slower, for demonstrated GPU memory pressure"
        ),
    )
    parser.add_argument(
        "--disable-ocr",
        action="store_true",
        default=env_flag("MARKER_DISABLE_OCR"),
        help="use only the PDF text layer; inappropriate for full conversion",
    )
    parser.add_argument(
        "--force-ocr",
        action="store_true",
        default=env_flag("MARKER_FORCE_OCR"),
        help=(
            "OCR every page even when a text layer exists; use for PDFs with "
            "a corrupt character map or unusable embedded OCR"
        ),
    )
    parser.add_argument(
        "--require-gpu",
        action="store_true",
        help="fail before conversion unless Marker sees a CUDA GPU",
    )
    parser.add_argument(
        "--reload-models-every",
        type=int,
        default=10,
        help=(
            "reuse one model bundle for this many sequential PDFs before "
            "reloading it (default: 10)"
        ),
    )
    parser.add_argument(
        "--legacy-per-document",
        action="store_true",
        help="start a fresh Marker process and reload models for every PDF",
    )
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    if args.reload_models_every < 1:
        parser.error("--reload-models-every must be at least 1")
    if args.disable_ocr and args.force_ocr:
        parser.error("--disable-ocr cannot be combined with --force-ocr")
    if args.require_gpu and args.disable_ocr:
        parser.error("--require-gpu cannot be combined with --disable-ocr")

    try:
        pairs = collect_pdfs(args.inputs)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    output_dir = args.output_dir.expanduser().resolve()
    if not pairs:
        parser.error("no PDF files found in the selected inputs")
    pending = [(pdf, relative) for pdf, relative in pairs
               if args.force or not (output_dir / relative.with_suffix(".md")).exists()]
    print(f"Found {len(pairs)} PDF(s); {len(pending)} pending; processing sequentially", flush=True)
    if args.dry_run:
        for pdf, relative in pairs:
            dest = output_dir / relative.with_suffix(".md")
            action = "convert" if args.force or not dest.exists() else "skip"
            print(f"would {action}: {pdf} -> {dest}")
        return 0
    if not pending:
        print("All reading copies already exist; use --force to regenerate.")
        return 0
    if not shutil.which("uvx"):
        parser.error("uvx is required for conversion; install uv from https://docs.astral.sh/uv/")

    gpu, error = cuda_probe(args.marker_package)
    if not gpu:
        print(
            "failed: could not prepare the selected Marker environment",
            file=sys.stderr,
        )
        if error:
            print(error, file=sys.stderr)
        return 1
    if args.require_gpu and not gpu.get("available"):
        print(
            "failed: the selected Marker environment cannot use CUDA",
            file=sys.stderr,
        )
        return 1
    if gpu.get("available"):
        print(
            f"GPU: {gpu['device']} via PyTorch {gpu['torch']} "
            f"({gpu['memory_gib']} GiB)",
            flush=True,
        )
    else:
        print(f"CUDA: unavailable; PyTorch {gpu['torch']} will use the upstream default device", flush=True)

    # The probe above materializes and validates the exact uv environment.
    # Reusing it offline avoids resolving the same dependency graph once per
    # PDF while leaving Marker and model behavior unchanged.
    os.environ.setdefault("UV_OFFLINE", "true")

    if args.minimum_memory:
        profile = f"minimum-memory (all six batches={args.batch_size})"
    else:
        profile = (
            "conservative profile "
            f"(four batches={args.batch_size}; OCR-error/table-rec CUDA defaults=14)"
        )
    if args.force_ocr:
        profile += "; forced full-page OCR"
    pipeline = "rough text-layer fallback" if args.disable_ocr else "full pipeline"
    print(f"Marker: {args.marker_package}; {pipeline}; {profile}", flush=True)
    if not args.legacy_per_document:
        print(
            "Execution: sequential persistent model host "
            f"(reload every {args.reload_models_every} documents)",
            flush=True,
        )
        success = convert_persistent(
            pairs,
            output_dir,
            args.force,
            args.marker_package,
            args.batch_size,
            args.minimum_memory,
            args.disable_ocr,
            args.force_ocr,
            args.reload_models_every,
        )
    else:
        print("Execution: legacy per-document model reload", flush=True)
        success = True
        for pdf, relative in pairs:
            dest = output_dir / relative.with_suffix(".md")
            success = convert(
                pdf,
                dest,
                args.force,
                args.marker_package,
                args.batch_size,
                args.minimum_memory,
                args.disable_ocr,
                args.force_ocr,
            ) and success
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
