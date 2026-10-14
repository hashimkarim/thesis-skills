#!/usr/bin/env python3
"""Install portable thesis skills for Codex and Claude Code (Python 3.10+)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"
STAMP = ".thesis-skills-install.json"
IGNORED = {"__pycache__", ".DS_Store", "Thumbs.db"}


def content_hashes(directory: Path) -> dict[str, str]:
    """Fingerprint contents without following links into other directories."""
    result = {}
    for base, dirs, files in os.walk(directory, followlinks=False):
        parent = Path(base)
        dirs[:] = sorted(name for name in dirs if name not in IGNORED)
        for name in list(dirs):
            path = parent / name
            if path.is_symlink():
                result[path.relative_to(directory).as_posix()] = "link:" + os.readlink(path)
                dirs.remove(name)
        for name in sorted(files):
            if name in IGNORED or name.endswith((".pyc", ".pyo")):
                continue
            path = parent / name
            relative = path.relative_to(directory).as_posix()
            if relative == STAMP:
                continue
            if path.is_symlink():
                result[relative] = "link:" + os.readlink(path)
            else:
                result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def receipt(directory: Path) -> dict | None:
    if directory.is_symlink() or not directory.is_dir():
        return None
    path = directory / STAMP
    if path.is_symlink():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (not isinstance(record, dict) or record.get("package") != "thesis-skills"
            or record.get("schema") != 1 or record.get("skill") != directory.name
            or not isinstance(record.get("files"), dict)):
        return None
    return record


def destinations(args: argparse.Namespace) -> list[Path]:
    if args.project and (args.codex_dir or args.claude_dir):
        raise ValueError("use --project or custom skill directories, not both")
    if args.agent == "codex" and args.claude_dir:
        raise ValueError("--claude-dir requires --agent claude or both")
    if args.agent == "claude" and args.codex_dir:
        raise ValueError("--codex-dir requires --agent codex or both")
    if args.project:
        project = args.project.expanduser().resolve()
        if not project.is_dir():
            raise ValueError(f"project directory does not exist: {project}")
        roots = {"codex": project / ".agents" / "skills",
                 "claude": project / ".claude" / "skills"}
    else:
        roots = {
            "codex": args.codex_dir or Path.home() / ".agents" / "skills",
            "claude": args.claude_dir or Path(os.environ.get("CLAUDE_CONFIG_DIR")
                                                      or Path.home() / ".claude") / "skills",
        }
    agents = ("codex", "claude") if args.agent == "both" else (args.agent,)
    return list(dict.fromkeys(roots[agent].expanduser().resolve() for agent in agents))


def plan_install(roots: list[Path], names: list[str], *, force: bool,
                 uninstall: bool) -> list[tuple[str, Path, Path]]:
    plan = []
    for root in roots:
        for name in names:
            source, target = SKILLS / name, root / name
            if target == source or source in target.parents or target in source.parents:
                raise ValueError(f"destination overlaps the source bundle: {target}")
            if not target.exists() and not target.is_symlink():
                action = "absent" if uninstall else "install"
            else:
                record = receipt(target)
                current = content_hashes(target) if record else None
                pristine = bool(record and current == record["files"])
                if uninstall:
                    if not record:
                        raise ValueError(f"refusing to uninstall an unmanaged skill: {target}")
                    if not pristine and not force:
                        raise ValueError(f"local edits in {target}; --force backs them up")
                    action = "remove" if pristine else "backup-remove"
                elif pristine and current == content_hashes(source):
                    action = "unchanged"
                elif pristine:
                    action = "update"
                elif force:
                    action = "replace"
                else:
                    raise ValueError(f"existing or edited skill: {target}; --force backs it up")
            plan.append((action, source, target))
    targets = [target for _, _, target in plan]
    if any(first in second.parents for first in targets for second in targets):
        raise ValueError("skill destinations overlap; choose separate skills directories")
    return plan


def backup(target: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    directory = target.parent.parent / ".thesis-skills-backups" / stamp
    directory.mkdir(parents=True)
    saved = directory / target.name
    target.rename(saved)
    print(f"backup: {saved}")
    return saved


def apply_action(action: str, source: Path, target: Path) -> None:
    if action in {"unchanged", "absent"}:
        return
    if action == "remove":
        shutil.rmtree(target)
        return
    if action == "backup-remove":
        backup(target)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".thesis-skills-stage-",
                                     dir=target.parent.parent) as temporary:
        staging = Path(temporary) / target.name
        shutil.copytree(source, staging, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", "*.pyo", ".DS_Store", "Thumbs.db"))
        record = {"schema": 1, "package": "thesis-skills", "skill": target.name,
                  "files": content_hashes(staging)}
        (staging / STAMP).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        saved = backup(target) if target.exists() or target.is_symlink() else None
        try:
            staging.rename(target)
        except OSError:
            if saved is not None:
                saved.rename(target)
            raise


def main(argv: list[str] | None = None) -> int:
    names = sorted(path.name for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("both", "codex", "claude"), default="both")
    parser.add_argument("--project", type=Path, help="install in an existing project")
    parser.add_argument("--codex-dir", type=Path, help="explicit Codex skills directory")
    parser.add_argument("--claude-dir", type=Path, help="explicit Claude skills directory")
    parser.add_argument("--skill", choices=names, action="append", help="select a skill; repeatable")
    parser.add_argument("--list", action="store_true", help="list bundled skills and exit")
    parser.add_argument("--dry-run", action="store_true", help="plan without writing anything")
    parser.add_argument("--force", action="store_true", help="back up conflicting local skills")
    parser.add_argument("--uninstall", action="store_true", help="remove only managed installs")
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(names))
        return 0
    selected = sorted(set(args.skill or names))
    try:
        for name in selected:
            source = SKILLS / name
            if source.is_symlink() or any(value.startswith("link:")
                                         for value in content_hashes(source).values()):
                raise ValueError(f"source skill contains a nonportable symlink: {source}")
        plan = plan_install(destinations(args), selected, force=args.force,
                            uninstall=args.uninstall)
        for action, source, target in plan:
            print(f"{'would ' if args.dry_run else ''}{action}: {target}")
            if not args.dry_run:
                apply_action(action, source, target)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if not args.dry_run and not args.uninstall:
        print("Done. Start a new assistant session if the skills do not appear.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
