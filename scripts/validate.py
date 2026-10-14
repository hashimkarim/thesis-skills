#!/usr/bin/env python3
"""Validate the portable bundle without installing third-party Python packages."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LINK = re.compile(r"\]\(<?([^\s)>]+)>?\)|(?:src|href)=[\"']([^\"']+)[\"']")
MACHINE_PATH = re.compile(r"/(?:home|Users|mnt)/[^\s`]+|[A-Za-z]:\\(?:Users|home)\\|thesis-workspace|RTX 4060|conda (?:run -n|activate) MIR")


def metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
    header = text.split("---", 2)[1]
    return dict(line.split(": ", 1) for line in header.strip().splitlines())


def main() -> int:
    errors = []
    skills = sorted((ROOT / "skills").iterdir())
    for skill in skills:
        try:
            if skill.is_symlink() or not skill.is_dir():
                raise ValueError(f"skill must be an ordinary directory: {skill.name}")
            fields = metadata(skill / "SKILL.md")
            if fields.get("name") != skill.name or not NAME.fullmatch(skill.name) or len(skill.name) > 64:
                raise ValueError(f"invalid/mismatched skill name: {skill.name}")
            if not 20 <= len(fields.get("description", "")) <= 1024:
                raise ValueError(f"missing or unsuitable description: {skill.name}")
            ui = (skill / "agents/openai.yaml").read_text(encoding="utf-8")
            interface = dict((key.strip(), json.loads(value)) for key, value in
                             (line.split(": ", 1) for line in ui.splitlines()[1:]))
            if not interface.get("display_name") or not 25 <= len(interface["short_description"]) <= 64:
                raise ValueError(f"invalid UI labels: {skill.name}")
            if "$" + skill.name not in interface.get("default_prompt", ""):
                raise ValueError(f"default prompt must name the skill: {skill.name}")
            if (skill / "LICENSE").read_bytes() != (ROOT / "LICENSE").read_bytes():
                raise ValueError(f"license copy differs: {skill.name}")
            for path in skill.rglob("*"):
                if path.is_symlink():
                    errors.append(f"nonportable symlink: {path.relative_to(ROOT)}")
                if path.suffix in {".md", ".py", ".yaml"}:
                    match = MACHINE_PATH.search(path.read_text(encoding="utf-8"))
                    if match:
                        errors.append(f"machine-specific content: {path.relative_to(ROOT)}: {match.group()}")
        except (OSError, ValueError, KeyError) as error:
            errors.append(str(error))

    paths = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *ROOT.glob("docs/*.md"),
             *ROOT.glob("skills/**/*.md")]
    for path in paths:
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for groups in LINK.findall(text):
            link = next(part for part in groups if part)
            if re.match(r"[a-z]+:", link) or link.startswith("#"):
                continue
            link = link.split("#", 1)[0]
            target = (path.parent / link).resolve()
            if not target.exists():
                errors.append(f"broken local link: {path.relative_to(ROOT)} -> {link}")
            if path.is_relative_to(ROOT / "skills"):
                skill = ROOT / "skills" / path.relative_to(ROOT / "skills").parts[0]
                if not target.is_relative_to(skill):
                    errors.append(f"skill depends on another folder: {path.relative_to(ROOT)} -> {link}")

    for path in [ROOT / "install.py", *ROOT.glob("scripts/*.py"), *ROOT.glob("tests/*.py"),
                 *ROOT.glob("skills/**/*.py")]:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            errors.append(str(error))
    try:
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        entry = marketplace["plugins"][0]
        if (plugin["name"] != "thesis-skills" or marketplace["name"] != plugin["name"]
                or entry["name"] != plugin["name"] or entry["source"] != "./"
                or entry["version"] != plugin["version"]):
            errors.append("plugin and marketplace metadata disagree")
    except (OSError, ValueError, KeyError, IndexError) as error:
        errors.append(str(error))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(skills)} self-contained skills, metadata, licenses, links, and Python syntax.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
