# Validation

Run from the repository with Python 3.10+:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Both commands use the standard library, so they can run without Marker, a GPU,
LaTeX, or an assistant subscription. If Claude Code is installed, also run
`claude plugin validate .` to check marketplace metadata with the host itself.

## What is checked

- Required skill metadata, directory names, Codex UI metadata, and license copies.
- Local Markdown/image links and self-contained skill resources.
- Machine-specific home/drive paths and old thesis-workspace assumptions in skills.
- Python syntax and consistent plugin/marketplace names and versions.
- Fresh, repeated, selected, moved, and project-local installations.
- Protection of existing skills and edits; backup, uninstall, and rollback behavior.
- PDF input discovery, output collisions, dependency-free dry runs and skips.
- Relative assets, missing/escaping images, source provenance, and rollback on failures.
- A worker plan that can be read from a separate process, including on Windows.

CI runs these on Linux, macOS, and Windows with Python 3.10 and 3.13. Symlink
tests skip where the operating system does not grant permission to create links.
Copies remain the normal install method.

## What these checks do not establish

No automated structural check proves that an assistant will make a sound
scholarly judgment. Try realistic tasks in a disposable project: a paragraph
with an unsupported claim, a scoped outline request, an inaccessible source, or
a different discipline and language. The assistant should honor scope, preserve
uncertainty, and use the new project's context rather than the original thesis.

Unit tests exercise converter orchestration and file handling without running
OCR models. To test full conversion, create a small document you can redistribute,
run the pinned converter in a scratch directory, inspect the source and Markdown,
and verify image links and provenance. Repeat for a relevant real document when
changing extraction behavior. Do not interpret a smoke test as an accuracy rate
or proof that all platforms support the upstream OCR stack.

After editing manuscript guidance, check that prompts distinguish a review,
outline, rewrite, and full evidence audit. After editing helpers, add a behavioral
test for the concrete failure or compatibility issue being fixed.
