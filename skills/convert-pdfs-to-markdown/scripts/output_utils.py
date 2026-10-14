"""Portable Markdown assets and rollback-safe publication, without Marker imports."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlsplit

IMAGE_REF_RE = re.compile(r"!\[([^\]]*)\]\(\s*(?:<([^>\n]*)>|((?:[^()\n]|\([^()\n]*\))+))\s*\)")
BROKEN_SUP_RE = re.compile(r"<sup>&</sup>lt;sup>([^<\n]+)</sup>")
DUPLICATE_TABLE_SEPARATOR_RE = re.compile(r"(?m)^(\|[-:| ]+\|)\n(?:\1\n)+")


def copy_markdown(src_md: Path, dest_md: Path) -> int:
    """Copy only referenced local images, keeping destinations relative and valid."""
    text = src_md.read_text(encoding="utf-8")
    root = src_md.parent.resolve()
    assets = dest_md.parent / f"{dest_md.stem}_assets"
    copied: dict[Path, str] = {}
    names: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        alt, angle, plain = match.groups()
        target = (angle if angle is not None else plain).strip()
        if target.startswith("#") or urlsplit(target).scheme in {"http", "https", "data"}:
            return match.group(0)
        source = (root / unquote(target)).resolve()
        if not source.is_relative_to(root):
            raise ValueError(f"image escapes the conversion directory: {target}")
        if not source.is_file():
            raise FileNotFoundError(f"missing extracted image: {target}")
        if source not in copied:
            assets.mkdir(parents=True, exist_ok=True)
            name = source.name
            number = 1
            while name.casefold() in names:
                name = f"{source.stem}_{number}{source.suffix}"
                number += 1
            names.add(name.casefold())
            shutil.copy2(source, assets / name)
            copied[source] = quote(f"{assets.name}/{name}", safe="/() -_.")
        return f"![{alt}](<{copied[source]}>)"

    dest_md.parent.mkdir(parents=True, exist_ok=True)
    text = IMAGE_REF_RE.sub(replace, text)
    text = BROKEN_SUP_RE.sub(r"<sup>\1</sup>", text)
    text = DUPLICATE_TABLE_SEPARATOR_RE.sub(r"\1\n", text)
    dest_md.write_text(text, encoding="utf-8")
    return len(copied)


def source_checksum(pdf: Path) -> str:
    digest = hashlib.sha256()
    with pdf.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def publish_output(src_md: Path, dest_md: Path, pdf: Path, settings: dict) -> int:
    """Prepare everything before replacing old output; restore it on a write failure."""
    dest_md.parent.mkdir(parents=True, exist_ok=True)
    targets = (dest_md, dest_md.parent / f"{dest_md.stem}_assets",
               dest_md.with_suffix(".source.json"))
    for index, target in enumerate(targets):
        if target.is_symlink():
            raise ValueError(f"refusing to replace a symlink output: {target}")
        if target.exists() and (target.is_dir() if index != 1 else not target.is_dir()):
            raise ValueError(f"unexpected output type: {target}")
    with tempfile.TemporaryDirectory(prefix=".marker-publish-", dir=dest_md.parent) as tmp:
        stage = Path(tmp)
        staged_md = stage / dest_md.name
        count = copy_markdown(src_md, staged_md)
        try:
            relative_pdf = Path(os.path.relpath(pdf, dest_md.parent)).as_posix()
        except ValueError:  # Different Windows drives: retain identity without leaking a home path.
            relative_pdf = None
        record = {
            "schema": 1, "source_pdf": relative_pdf, "source_filename": pdf.name,
            "source_sha256": source_checksum(pdf),
            "converted_at": datetime.now(timezone.utc).isoformat(),
            "settings": settings, "quality_check": "not-reviewed",
        }
        (stage / targets[2].name).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        saved: list[tuple[Path, Path]] = []
        published: list[Path] = []
        try:
            for index, target in enumerate(targets):
                if target.exists():
                    old = stage / f"previous-{index}"
                    target.rename(old)
                    saved.append((old, target))
            for target in targets:
                replacement = stage / target.name
                if replacement.exists():
                    replacement.rename(target)
                    published.append(target)
        except OSError:
            for target in reversed(published):
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            for old, target in saved:
                old.rename(target)
            raise
    return count
