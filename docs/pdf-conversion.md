# PDF conversion

The bundled wrapper runs the full native pipeline from `marker-pdf==1.10.1`.
It preserves the original PDF and creates a Markdown reading copy, extracted
images, and a provenance record. It can run from the repository or from an
installed skill folder; helpers resolve from their own location.

## Requirements

- Python 3.10+ for the wrapper.
- [uv, including uvx](https://docs.astral.sh/uv/getting-started/installation/), on PATH.
- An environment compatible with the pinned Marker/PyTorch packages.
- Network access for the first package and model downloads, and enough disk,
  RAM, and optionally VRAM for the selected documents.

The wrapper uses `uvx --from marker-pdf==1.10.1` to isolate conversion packages.
It does not pip-install them into your thesis environment. Marker and its model
weights are external dependencies with their own licenses and requirements;
see the [upstream project](https://github.com/datalab-to/marker).

The lightweight installer and tests target Linux, macOS, and Windows. That does
not establish full OCR compatibility or GPU acceleration on every platform.
The GPU check specifically requires **CUDA**, not Apple MPS. Without
`--require-gpu`, the wrapper permits the device behavior of the installed
Marker/PyTorch environment; CPU execution can be much slower. Consult upstream
support for your hardware rather than assuming the wrapper supplies drivers.

## Preview and convert

From the bundle checkout:

```bash
python3 skills/convert-pdfs-to-markdown/scripts/convert.py "papers" --output-dir "reading-copies" --dry-run
python3 skills/convert-pdfs-to-markdown/scripts/convert.py "papers" --output-dir "reading-copies"
```

Input can be one or more PDF paths or directories. Quote paths with spaces.
Directory inputs preserve subdirectories. When multiple inputs would produce
the same output path, conversion fails before any package setup. Use one common
input root or separate output directories. Duplicate references to the same
source are processed once. An empty or missing input is reported as an error.

`--dry-run` does not write output, download packages, load models, or check CUDA.
An invocation whose outputs already exist also skips dependency setup.

For an installed skill, replace the repository script path with the path printed
by the installer, ending in `convert-pdfs-to-markdown/scripts/convert.py`.
The assistant can resolve that location from its skill catalog. No hardcoded
checkout path is embedded in the scripts.

## Options

| Option | Purpose |
| --- | --- |
| `--force` | Regenerate an existing reading copy; inspect hand edits first |
| `--force-ocr` | OCR every page when the embedded character map/text is defective |
| `--require-gpu` | Fail if the pinned environment cannot use CUDA |
| `--minimum-memory` | Also constrain OCR-error and table-recognition batches |
| `--batch-size N` | Set the four constrained batch sizes; default 1 |
| `--reload-models-every N` | Reload after N sequential PDFs; default 10 |
| `--legacy-per-document` | Load a new model process per PDF for diagnosis |
| `--disable-ocr` | Explicitly rough text-layer fallback, unsuitable for scans |
| `--marker-package SPEC` | Explicit version override; compatibility must be tested |

The persistent worker retries a CUDA out-of-memory error once using all six
batch sizes of one. This does not remove recognition stages. Run one converter
at a time; concurrent jobs compete for the same memory. The per-document
diagnostic mode does not include that automatic retry.

The package can also be set through `MARKER_PACKAGE`; `MARKER_FORCE_OCR` and
`MARKER_DISABLE_OCR` accept `1`, `true`, or `yes`. CLI help lists the available
flags. Contradictory OCR options are rejected. Keep the pinned version unless
you intentionally test an override: this worker calls the 1.10.1 Python API.
The pin selects Marker itself, not a lock of every transitive dependency.

## Outputs and verification

```text
reading-copies/
  paper.md
  paper_assets/
    figure.png
  paper.source.json
```

The sidecar records a source path relative to the output directory, original
filename, SHA-256, timestamp, and conversion settings. On different Windows
drives, a relative path may not exist; the path is null and the filename/checksum
remain. Move the PDF and reading copies together to preserve links, or use the
checksum to recover the source after relocation. The record starts as
`quality_check: not-reviewed`; machine conversion is not human verification.

Existing output is replaced only after new Markdown, assets, and provenance have
been prepared. A reported conversion failure preserves the prior copy. Final
file replacements roll back on ordinary write errors; abrupt process or machine
termination during the replacement window is not a transaction guarantee.

Inspect representative PDF pages against the extraction: reading order, section
structure, tables, equations, citations, notes, and image references. Record the
pages checked and unresolved defects in your project notes. Fix malformed parts
locally without changing the source's meaning. Mechanical cleanup handles a
known escaped-superscript form and consecutive duplicate table separators.

Use clear checked Markdown for everyday paraphrases. Verify quotations, numbers,
equations, uncertain metadata, and extraction defects against the original.
Inspect the rendered page when the text layer is unreliable. Cite the original
publication and reuse checks when the relevant evidence has not changed.

## Troubleshooting

- **uvx missing:** install uv using its official instructions and reopen the shell.
- **CUDA unavailable:** check the driver and PyTorch environment; omit the
  requirement only if CPU/other upstream-supported execution is acceptable.
- **Out of memory:** use `--minimum-memory`, smaller documents, or a machine with
  more memory. Do not turn off OCR silently.
- **Corrupt text:** rerun the affected document with `--force --force-ocr` and
  compare source pages. Digital PDFs with good text do not need forced OCR.
- **Broken/missing image:** conversion fails rather than publishing a dangling
  local image link. Inspect the upstream extraction or use another converter.
- **Failed model download:** check network/cache availability. Offline package
  reuse does not mean the model weights are already cached.
