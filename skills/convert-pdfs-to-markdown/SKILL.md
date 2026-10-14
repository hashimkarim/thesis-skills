---
name: convert-pdfs-to-markdown
description: Convert scholarly or technical PDFs into local Markdown reading copies with extracted images and traceable sources, or diagnose and repair poor PDF extraction.
---

# Convert PDFs to Markdown

Preserve the PDF as the canonical source. Use checked Markdown for ordinary
reading and paraphrasing. Check the PDF for exact details or extraction defects.
Read project instructions and `THESIS.md` if present; resolve project paths from
that brief and bundled script paths from this skill's own directory.

## Convert

Use a maintained project converter when one exists and meets the task. Otherwise
run this skill's bundled `scripts/convert.py` with Python 3.10+ and `uvx` on PATH:

```bash
python /path/to/this/skill/scripts/convert.py "papers" --output-dir "literature/markdown" --dry-run
python /path/to/this/skill/scripts/convert.py "papers" --output-dir "literature/markdown"
```

Replace `/path/to/this/skill` with the directory containing this `SKILL.md` as
reported by the host. It is not a literal installation path. Quote paths with
spaces. No particular home directory, conda environment, or repository is needed.

The wrapper pins `marker-pdf==1.10.1` and runs documents sequentially with the
full native pipeline: layout, text detection, selective OCR, equations, tables,
images, and Markdown. The first real run may download packages and model weights.
The writing skills and a conversion dry run need neither downloads nor a GPU.

The default limits four model batches to one and keeps the pinned release's
OCR-error/table defaults. It reuses models for ten documents at a time. Batch
sizes change throughput and memory use, not which extraction stages run.

- Add `--require-gpu` when CUDA is required. It checks the exact Marker environment.
  CPU conversion is allowed without that flag and can be substantially slower.
- Use `--minimum-memory` after observed memory pressure. The persistent worker
  retries a document once with all batches set to one after a CUDA OOM.
- Use `--force --force-ocr` for a demonstrated corrupt character map or bad
  embedded text layer. Do not force OCR across a corpus without a reason.
- Existing Markdown is skipped. `--force` requests regeneration; failed
  conversion preserves the previous output. Inspect any hand edits first.
- `--legacy-per-document` starts a fresh model process per PDF for diagnosis.
- `--disable-ocr` is an explicitly rough text-layer fallback. Record that choice.
  Do not silently use it in place of full conversion.
- A different Marker version requires an explicit, tested `--marker-package`
  override. Newer major versions may not support this worker's API.

Run one converter at a time. Review RAM/VRAM for long jobs using available OS
tools; `nvidia-smi` is useful on NVIDIA systems but is not an installation check
for every platform. Do not start simultaneous Marker jobs to accelerate a batch.

## Check the result

Inspect representative source pages and the corresponding Markdown. Check
reading order, headings, lists, tables, equations, citations, footnotes, and
image links. Record checked pages and unresolved defects; conversion success
does not prove extraction accuracy. A machine provenance file records the source
mapping, not human QA.

Apply targeted cleanup to malformed passages without changing their meaning.
For exact quotations, numerical values, equations, uncertain bibliographic
details, or ambiguous text, verify the original PDF. Inspect its rendered page
when OCR is doubtful. Reuse checks when source and claim scope are unchanged.

If quality remains poor, compare another suitable local converter and record
the difference. Rough text extraction is a fallback for discovery, not verified
quotation. Cite the original publication, not the Markdown conversion.

## Output

Each source produces `<name>.md`, optional `<name>_assets/` images, and
`<name>.source.json` with the relative source path, checksum, and conversion
settings. Directory inputs retain relative subdirectories. Conflicting output
names fail before conversion; choose a common input root or separate output
directories. Image links are relative and angle-wrapped for spaces and punctuation.
