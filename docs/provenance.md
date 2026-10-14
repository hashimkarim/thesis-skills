# Origins and redistribution

This bundle grew out of Hashim Karim's thesis workflow. It packages reusable
guidance rather than the thesis, its literature collection, or private feedback.

| Content | Origin and treatment |
| --- | --- |
| `thesis-writing` and its manuscript guide | Adapted from the maintainer's custom skill; preserved narrative, voice, source-checking, and evidence guidance; removed personal paths, field-specific requirements, and private document references |
| `convert-pdfs-to-markdown` and Marker helpers | Adapted from the maintainer's custom conversion workflow; made dry runs lightweight, plans portable, names collision-aware, assets relative, and replacements recoverable |
| Research, citation, and presentation skills | Focused reusable workflows developed from the existing writing skill's research, source, and presentation guidance |
| Literature-review and LaTeX skills | Companion workflows authored for this portable package |
| Installer, project brief, tests, CI, documentation, and banner | Authored for this repository |

The original writing workflow was informed by Jan van Gemert's research,
writing, and presentation guidance, Simon Peyton Jones's *How to write a great
research paper*, and lessons from thesis revision. This package is not an
official university guide or an endorsement by those authors. It includes
adapted instructions, not copies of their PDFs or slide decks.

No proprietary or account-synced Claude/OpenAI skills are redistributed. Both
assistants use the same package-owned skill folders, with optional Codex UI
metadata and a Claude Code marketplace manifest. Host-specific bundled skills
remain separately installed and licensed by their providers.

The repository's instructions and helper code are MIT licensed; each skill also
carries a license copy so it can be transferred independently. Marker, PyTorch,
uv, TeX tools, model weights, and papers retain their respective terms. They are
not included in the repository. Users provide their own sources and project
requirements. Source attribution is not a claim that this bundle has access to
the original private materials.
