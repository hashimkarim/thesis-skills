---
name: thesis-latex
description: Edit, build, and troubleshoot a LaTeX thesis, including bibliography integration, figures, tables, cross-references, and submission formatting within the existing template.
---

# Thesis LaTeX

Inspect applicable `AGENTS.md`, `CLAUDE.md`, and `THESIS.md` instructions. Resolve
brief paths relative to the brief. Locate the real entry document, included
chapters, bibliography, class, build script, and output directory before editing.
Do not assume `main.tex`, a particular institution, or a specific TeX engine.

## Preserve the project

Use the maintained template and build configuration (`latexmkrc`, Makefile,
Tectonic configuration, editor recipes, or documented commands). Inspect scripts
before running them. Do not replace class files, change engines, enable shell
escape, or install a large TeX distribution merely to fix a sentence.

Edit source files, not generated PDFs, auxiliary files, or converted manuscript
copies. Retain custom commands, citation style, label conventions, and language
settings. Escape special characters when inserting prose, while preserving
intentional math and commands. Avoid broad regular-expression rewrites of TeX.

## Integrate content

- Keep equations grammatical, define symbols, and retain units and notation.
- Place stable labels appropriately with captions and preserve references when
  moving content. Use the project's existing reference commands.
- Use real data for result plots and keep their generation provenance. Label
  conceptual or hypothetical illustrations clearly. Prefer vector output for
  diagrams where suitable and inspect readability at the final printed size.
- Make captions explain what is shown and what the evidence permits the reader
  to conclude. Check figure/table placement, scaling, axes, legends, and units.
- Preserve bibliography keys and the existing BibTeX or Biber workflow. Do not
  invent missing citation metadata to make a build succeed.

## Validate proportionately

Run the documented build after changes that can affect the document. If no
workflow exists, identify the intended engine before proposing a command such
as `latexmk -pdf main.tex`; that command is an example, not a universal default.
Review errors, undefined references/citations, missing glyphs, and material
overfull boxes. Inspect affected rendered pages for clipping and layout defects.

A successful exit does not prove visual correctness or compliance with a
university's rules. For submission checks, use the actual current requirements
provided by the project or institution, including accessibility when required.
Report the command run, output artifact, remaining issues, and any unavailable
tool. Do not claim a successful build when the TeX environment is missing.
