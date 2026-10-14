---
name: thesis-citations
description: Audit thesis claims and citations, verify bibliography metadata and source passages, and repair unsupported attribution without inventing references.
---

# Thesis claims and citations

Read applicable instructions and the project's `THESIS.md` if available. Resolve
configured manuscript, bibliography, evidence-note, and literature paths from
that file. Preserve the project's citation style and existing keys.

## Scope the check

Audit the requested text, new or substantively changed factual claims, and
unsupported or questioned premises encountered there. A style edit does not
require a new whole-thesis audit. Reuse existing passage checks while source
version and claim scope remain unchanged.

Distinguish external factual claims, original findings, implementation facts,
proposals, and explicitly hypothetical examples. Each needs the appropriate
support; not every sentence needs a literature citation. Check external premises
inside sentences about original work separately.

## Verify support

1. Read the cited passage in context. Check population, task, modality, comparison,
   direction, and strength of evidence. A topically related title is insufficient.
2. Use quality-checked Markdown for ordinary paraphrases. Check the original PDF
   or publisher for quotations, numbers, equations, tables, uncertain metadata,
   and extraction problems. Inspect the rendered page when text extraction is
   doubtful. Record a missing or inaccessible source instead of claiming a check.
3. Verify author, title, year, venue, and DOI against the actual publication or
   authoritative metadata. Distinguish a preprint from a later published version.
   Do not guess a DOI or use a resolver URL as evidence of the paper's findings.
4. Preserve quotation boundaries and page locators. Match paraphrases to the
   actual claim and retain necessary qualifications. Do not convert correlation
   into causation or an engineering target into a measured human threshold.
5. Place citations next to the supported claims. A citation may support a bounded
   group of sentences; do not repeat it mechanically or add unrelated references.

## Resolve and report

For each material problem, give the claim location, evidence inspected, issue,
and a supported correction or explicit evidence gap. Narrow, remove, or label
an inference when direct support is absent. Do not silently supply a stronger
claim or invented experiment. Original results need traceable figures, tables,
or artifacts, not a spurious external reference.

When editing a bibliography, inspect for duplicate records, key collisions,
unresolved citations, and accidental key changes. Preserve capitalization and
characters required by the existing BibTeX/BibLaTeX workflow. Compile through the
project's normal build if available; report checks that could not run. For a
small audit, concise notes suffice; do not impose a per-sentence database.
