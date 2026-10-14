import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import install

ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="thesis skills test ")
        self.addCleanup(self.temp.cleanup)
        # Normalize OS-provided temporary-directory aliases before comparisons.
        self.project = Path(self.temp.name).resolve() / "Research project with spaces"
        self.project.mkdir()

    def run_cli(self, *args, expected=0, installer=None):
        result = subprocess.run([sys.executable, str(installer or ROOT / "install.py"),
                                 "--project", str(self.project), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def target(self, name="thesis-writing", agent=".agents"):
        return self.project / agent / "skills" / name

    def test_installs_complete_independent_copies_for_both_agents(self):
        self.run_cli()
        for agent in (".agents", ".claude"):
            for source in install.SKILLS.iterdir():
                target = self.target(source.name, agent)
                self.assertTrue((target / "SKILL.md").is_file())
                self.assertEqual(install.content_hashes(source), install.content_hashes(target))
                self.assertIsNotNone(install.receipt(target))
                self.assertFalse(target.is_symlink())

    def test_dry_run_creates_nothing(self):
        self.run_cli("--dry-run")
        self.assertEqual(list(self.project.iterdir()), [])

    def test_repeat_install_is_idempotent(self):
        self.run_cli()
        before = (self.target() / "SKILL.md").stat().st_mtime_ns
        result = self.run_cli()
        self.assertIn("unchanged:", result.stdout)
        self.assertEqual(before, (self.target() / "SKILL.md").stat().st_mtime_ns)
        self.assertFalse(list(self.project.rglob(".thesis-skills-backups")))

    def test_select_one_skill_and_agent(self):
        self.run_cli("--agent", "claude", "--skill", "thesis-citations")
        self.assertFalse((self.project / ".agents").exists())
        self.assertEqual([p.name for p in (self.project / ".claude/skills").iterdir()],
                         ["thesis-citations"])

    def test_preflight_conflict_does_not_partially_install(self):
        target = self.target(agent=".claude")
        target.mkdir(parents=True)
        (target / "custom.md").write_text("keep")
        self.run_cli(expected=1)
        self.assertFalse((self.project / ".agents").exists())
        self.assertEqual((target / "custom.md").read_text(), "keep")

    def test_force_preserves_foreign_content_in_backup(self):
        target = self.target()
        target.mkdir(parents=True)
        (target / "custom.md").write_text("keep")
        self.run_cli("--force")
        backups = list(self.project.rglob("custom.md"))
        self.assertEqual(len(backups), 1)
        self.assertIn(".thesis-skills-backups", str(backups[0]))
        self.assertEqual(backups[0].read_text(), "keep")

    def test_local_edit_prevents_update_and_uninstall(self):
        self.run_cli()
        (self.target() / "SKILL.md").write_text("my changes")
        self.run_cli(expected=1)
        self.run_cli("--uninstall", expected=1)
        self.assertTrue(self.target(agent=".claude").exists())
        self.run_cli("--uninstall", "--force")
        saved = list(self.project.rglob("SKILL.md"))
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].read_text(), "my changes")

    def test_uninstall_preserves_unrelated_skills(self):
        self.run_cli()
        unrelated = self.target("unrelated")
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("unrelated")
        self.run_cli("--uninstall")
        self.assertEqual((unrelated / "SKILL.md").read_text(), "unrelated")
        self.assertFalse(self.target().exists())

    def test_force_never_uninstalls_unmanaged_skill(self):
        self.target().mkdir(parents=True)
        self.run_cli("--uninstall", "--force", expected=1)
        self.assertTrue(self.target().exists())

    def test_relocated_checkout_and_project_need_no_original_paths(self):
        moved = Path(self.temp.name) / "Moved bundle"
        shutil.copytree(ROOT, moved, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.run_cli(installer=moved / "install.py")
        changed = moved / "skills/thesis-writing/SKILL.md"
        changed.write_text(changed.read_text() + "\nAn upstream improvement.\n")
        result = self.run_cli(installer=moved / "install.py")
        self.assertIn("update:", result.stdout)
        shutil.rmtree(moved)
        project2 = self.project.with_name("Another machine")
        self.project.rename(project2)
        script = project2 / ".agents/skills/convert-pdfs-to-markdown/scripts/convert.py"
        result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("upstream improvement", (project2 / ".agents/skills/thesis-writing/SKILL.md").read_text())

    def test_symlink_target_is_backed_up_without_editing_its_source(self):
        original = Path(self.temp.name) / "Original skill"
        original.mkdir()
        (original / "SKILL.md").write_text("original")
        self.target().parent.mkdir(parents=True)
        try:
            self.target().symlink_to(original, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation unavailable")
        self.run_cli("--force")
        self.assertEqual((original / "SKILL.md").read_text(), "original")
        self.assertFalse(self.target().is_symlink())

    def test_user_destinations_and_explicit_legacy_directory(self):
        args = argparse.Namespace(project=None, codex_dir=None, claude_dir=None, agent="both")
        with patch.object(Path, "home", return_value=self.project), patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": ""}):
            self.assertEqual(install.destinations(args), [self.project / ".agents/skills", self.project / ".claude/skills"])
            args.codex_dir = self.project / ".codex/skills"
            self.assertEqual(install.destinations(args)[0], args.codex_dir)

    def test_project_brief_never_overwrites(self):
        command = [sys.executable, str(ROOT / "scripts/init_project.py"), str(self.project)]
        self.assertEqual(subprocess.run(command + ["--dry-run"], capture_output=True).returncode, 0)
        self.assertFalse((self.project / "THESIS.md").exists())
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        (self.project / "THESIS.md").write_text("custom brief")
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual((self.project / "THESIS.md").read_text(), "custom brief")

    def test_failed_replacement_restores_original_install(self):
        self.run_cli()
        previous = (self.target() / "SKILL.md").read_bytes()
        rename = Path.rename

        def fail_stage(path, target):
            if path.parent.name.startswith(".thesis-skills-stage-"):
                raise OSError("simulated disk failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_stage), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(OSError):
                install.apply_action("update", install.SKILLS / "thesis-writing", self.target())
        self.assertEqual((self.target() / "SKILL.md").read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
