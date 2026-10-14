import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/convert-pdfs-to-markdown/scripts"
sys.path.insert(0, str(SCRIPTS))
import convert
import output_utils


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="paper conversion ")
        self.addCleanup(self.temp.cleanup)
        # macOS /var aliases and Windows short names refer to the same directory.
        self.root = Path(self.temp.name).resolve()
        self.pdf = self.root / "Example paper.pdf"
        self.pdf.write_bytes(b"%PDF-test fixture")
        self.source = self.root / "extracted"
        self.source.mkdir()
        self.md = self.source / "paper.md"
        self.md.write_text("# A paper\n", encoding="utf-8")
        self.dest = self.root / "reading copies" / "Example paper.md"

    def cli(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / "convert.py"),
                                 str(self.pdf), "--output-dir", str(self.dest.parent), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_dry_run_never_initializes_marker(self):
        args = ["convert.py", str(self.pdf), "--output-dir", str(self.dest.parent), "--dry-run"]
        with patch.object(sys, "argv", args), patch.object(convert, "cuda_probe") as probe:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(convert.main(), 0)
            probe.assert_not_called()
        self.assertFalse(self.dest.parent.exists())

    def test_existing_output_skips_without_dependencies(self):
        self.dest.parent.mkdir()
        self.dest.write_text("keep")
        args = ["convert.py", str(self.pdf), "--output-dir", str(self.dest.parent)]
        with patch.object(sys, "argv", args), patch.object(convert, "cuda_probe") as probe:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(convert.main(), 0)
            probe.assert_not_called()

    def test_nested_paths_and_duplicate_inputs(self):
        directory = self.root / "collection"
        (directory / "nested").mkdir(parents=True)
        pdf = directory / "nested/paper.PDF"
        pdf.write_bytes(b"pdf")
        pairs = convert.collect_pdfs([directory, directory])
        self.assertEqual(pairs, [(pdf, Path("nested/paper.PDF"))])

    def test_output_collisions_fail_before_conversion(self):
        other = self.root / "other"
        other.mkdir()
        pdf = other / self.pdf.name.upper()
        pdf.write_bytes(b"pdf")
        with self.assertRaisesRegex(ValueError, "collision"):
            convert.collect_pdfs([self.pdf, pdf])

    def test_asset_directory_cannot_overlap_another_document(self):
        assets = self.root / "Example paper_assets"
        assets.mkdir()
        (assets / "nested.pdf").write_bytes(b"pdf")
        with self.assertRaisesRegex(ValueError, "overlap"):
            convert.collect_pdfs([self.root])

    def test_missing_source_has_actionable_error(self):
        self.pdf.unlink()
        self.assertIn("Not a PDF", self.cli("--dry-run", expected=2).stderr)

    def test_empty_directory_is_not_silent_success(self):
        self.pdf.unlink()
        self.pdf.mkdir()
        self.assertIn("no PDF", self.cli("--dry-run", expected=2).stderr)

    def test_spaced_parenthesized_images_remain_relative(self):
        (self.source / "figure (1).png").write_bytes(b"image")
        self.md.write_text("![plot](<figure (1).png>)\n![same](figure%20%281%29.png)\n", encoding="utf-8")
        self.assertEqual(output_utils.copy_markdown(self.md, self.dest), 1)
        text = self.dest.read_text()
        self.assertEqual(text.count("<Example paper_assets/figure (1).png>"), 2)
        self.assertEqual((self.dest.parent / "Example paper_assets/figure (1).png").read_bytes(), b"image")

    def test_distinct_images_with_same_name_are_not_overwritten(self):
        for name in ("a", "b"):
            (self.source / name).mkdir()
            (self.source / name / "image.png").write_text(name)
        self.md.write_text("![](a/image.png)\n![](b/image.png)\n")
        self.assertEqual(output_utils.copy_markdown(self.md, self.dest), 2)
        self.assertEqual({p.read_text() for p in (self.dest.parent / "Example paper_assets").iterdir()}, {"a", "b"})

    def test_missing_and_escaping_assets_fail_without_replacing_old_copy(self):
        self.dest.parent.mkdir()
        self.dest.write_text("old copy")
        for reference in ("missing.png", "../Example%20paper.pdf"):
            self.md.write_text(f"![]({reference})")
            with self.assertRaises((ValueError, FileNotFoundError)):
                output_utils.publish_output(self.md, self.dest, self.pdf, {})
            self.assertEqual(self.dest.read_text(), "old copy")

    def test_publish_records_relative_source_checksum_and_settings(self):
        output_utils.publish_output(self.md, self.dest, self.pdf, {"force_ocr": True})
        record = json.loads(self.dest.with_suffix(".source.json").read_text())
        self.assertEqual((self.dest.parent / record["source_pdf"]).resolve(), self.pdf)
        self.assertEqual(record["source_sha256"], output_utils.source_checksum(self.pdf))
        self.assertEqual(record["quality_check"], "not-reviewed")
        self.assertEqual(record["settings"], {"force_ocr": True})

    def test_publish_removes_stale_assets_only_on_success(self):
        old = self.dest.parent / "Example paper_assets"
        old.mkdir(parents=True)
        (old / "old.png").write_bytes(b"old")
        self.dest.write_text("old copy")
        output_utils.publish_output(self.md, self.dest, self.pdf, {})
        self.assertFalse(old.exists())
        self.assertEqual(self.dest.read_text(), "# A paper\n")

    def test_failed_force_conversion_preserves_original(self):
        self.dest.parent.mkdir()
        self.dest.write_text("old copy")
        with patch.object(convert.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertFalse(convert.convert(self.pdf, self.dest, True, convert.DEFAULT_MARKER_PACKAGE, 1, False, False, False))
        self.assertEqual(self.dest.read_text(), "old copy")

    def test_unexpected_output_directory_is_not_replaced(self):
        self.dest.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "output type"):
            output_utils.publish_output(self.md, self.dest, self.pdf, {})
        self.assertTrue(self.dest.is_dir())

    def test_output_symlink_is_not_followed(self):
        self.dest.parent.mkdir()
        original = self.root / "unrelated.md"
        original.write_text("keep")
        try:
            self.dest.symlink_to(original)
        except OSError:
            self.skipTest("symlink creation unavailable")
        with self.assertRaisesRegex(ValueError, "symlink"):
            output_utils.publish_output(self.md, self.dest, self.pdf, {})
        self.assertEqual(original.read_text(), "keep")

    def test_publish_rolls_back_when_a_rename_fails(self):
        output_utils.publish_output(self.md, self.dest, self.pdf, {})
        previous = self.dest.with_suffix(".source.json").read_bytes()
        self.md.write_text("new copy")
        rename = Path.rename

        def fail_metadata(path, target):
            if path.name.endswith(".source.json") and path.parent.name.startswith(".marker-publish-"):
                raise OSError("simulated disk failure")
            return rename(path, target)

        with patch.object(Path, "rename", fail_metadata), self.assertRaises(OSError):
            output_utils.publish_output(self.md, self.dest, self.pdf, {})
        self.assertEqual(self.dest.read_text(), "# A paper\n")
        self.assertEqual(self.dest.with_suffix(".source.json").read_bytes(), previous)

    def test_worker_plan_is_readable_by_another_process(self):
        def worker(command, **kwargs):
            path = Path(command[command.index("--plan") + 1])
            result = subprocess.run([sys.executable, "-c", "import pathlib,sys; print(pathlib.Path(sys.argv[1]).read_text())", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)[0]["pdf"], str(self.pdf))
            self.assertIn("--marker-package", command)
            return subprocess.CompletedProcess(command, 0)

        real_run = subprocess.run
        def fake_run(command, **kwargs):
            if command[0] == "uvx":
                with patch.object(subprocess, "run", real_run):
                    return worker(command, **kwargs)
            return real_run(command, **kwargs)

        with patch.object(convert.subprocess, "run", side_effect=fake_run):
            self.assertTrue(convert.convert_persistent([(self.pdf, Path(self.pdf.name))], self.dest.parent,
                False, convert.DEFAULT_MARKER_PACKAGE, 1, False, False, False, 10))

    def test_invalid_ocr_options_fail_before_dependency_setup(self):
        self.cli("--disable-ocr", "--force-ocr", "--dry-run", expected=2)


if __name__ == "__main__":
    unittest.main()
