#!/usr/bin/env python3
"""Create a portable THESIS.md brief without changing existing project files."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="existing thesis project directory")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"project directory does not exist: {project}")
    destination = project / "THESIS.md"
    if destination.exists() or destination.is_symlink():
        parser.error(f"refusing to overwrite {destination}; edit the existing brief")
    if args.dry_run:
        print(f"would create: {destination}")
        return 0
    template = Path(__file__).resolve().parents[1] / "examples" / "THESIS.md"
    with destination.open("x", encoding="utf-8", newline="\n") as output:
        output.write(template.read_text(encoding="utf-8"))
    print(f"created: {destination}; customize the audience, paths, and commands")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
