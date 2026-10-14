# Choosing a skill

In Codex, mention `$skill-name`. With copied Claude Code skills, use
`/skill-name`. With the Claude plugin, use `/thesis-skills:skill-name`.
Ordinary requests can also match a skill's description automatically; explicitly
naming it makes your choice clear.

## Writing

```text
Use $thesis-writing to review chapter 2 against THESIS.md.
Keep my voice. Identify concept-order problems and propose a section outline.
```

This skill preserves the substantial manuscript guide: reader questions,
connected paragraphs, examples before machinery, contribution boundaries,
captions, and a final comprehension pass. It can draft or edit when requested;
an outline-only request stays an outline.

## PDF reading copies

```text
Use $convert-pdfs-to-markdown on the PDFs listed in THESIS.md.
Show the conversion plan, convert the new files, and check representative pages.
```

The helper preserves source files, extracts referenced images, and records source
checksums and settings. QA is a separate step. See [conversion](pdf-conversion.md).

## Literature review

```text
Use $thesis-literature-review to compare the papers in my literature folder.
Organize by the assumptions and evaluation settings relevant to my research question.
Show which comparison cells still need source verification.
```

Use the optional [reading-note template](../skills/thesis-literature-review/assets/reading-note.md)
when it helps. The skill distinguishes a scoped narrative review from an
exhaustive systematic review and does not invent missing findings.

## Research design

```text
Use $thesis-research to review this proposed study.
Identify the claims each comparison can support, confounders, and evidence gaps.
```

Adapt study design to the discipline. A qualitative, theoretical, or historical
thesis does not need to become a machine-learning benchmark.

## Citations and claims

```text
Use $thesis-citations to audit the new claims in section 3.2.
Check passages and scope, preserve existing citation keys, and flag unsupported claims.
```

Expect source locations and concrete repairs, not extra citations chosen from
titles alone. Exact numbers and quotations need original-source checks.

## LaTeX

```text
Use $thesis-latex to integrate this figure and caption into the existing template.
Use the documented build, check references, and inspect the affected PDF page.
```

This skill respects the existing engine, class, macros, and bibliography backend.
It does not ship TeX or silently install a distribution.

## Presentation and defense

```text
Use $thesis-presentation to plan a 20-minute defense for the audience in THESIS.md.
Give slide purposes, evidence to show, speaker notes, and likely questions.
```

Ask for the output you need: outline, slide text, a visual brief, feedback on a
deck, or rendered slides when the assistant has the necessary tools. It must not
claim to have rendered a deck when it produced only content.

## Combining skills

Read and check literature before using it to support an argument. Review the
research logic before polishing an unsupported conclusion. Apply LaTeX mechanics
after the substantive text is settled. For a small task, use only the relevant
skill; this is a toolbox, not a mandatory seven-step process.
