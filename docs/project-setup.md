# Adapt the skills to a thesis

Keep reusable skill instructions separate from the specifics of one thesis.
The optional [`THESIS.md` template](../examples/THESIS.md) records your audience,
research question, language, file locations, evidence, and build workflow.

From the bundle checkout:

```bash
python3 scripts/init_project.py "../my-thesis"
```

The command creates one file and refuses to replace an existing brief. It does
not create the example directories or modify `AGENTS.md` or `CLAUDE.md`.
Edit the brief before asking an assistant to use it. Alternatively, keep the
same information in existing project instructions and point the assistant there.

## Paths and multiple repositories

Paths in the brief are relative to the directory containing `THESIS.md`.
The skill installation directory never determines where a manuscript lives.
Use explicit relative paths for a project spread across sibling repositories:

```text
research/
  THESIS.md
  manuscript/
  literature/
  experiments/
```

For a brief inside `manuscript/`, use `../literature/` and `../experiments/`.
When transferring the project, preserve that relationship or update the brief.
Launch the assistant in the project and mention the brief's path when it is
outside the current repository; hosts may stop ancestor discovery at Git roots.

## What to customize

State the actual discipline and audience. The workflow supports a layered
explanation but does not mandate an engineering reader, a particular university,
or a fixed chapter order. Record the author's voice and institutional citation
or formatting requirements. Use current requirements instead of assuming those
from another thesis apply.

Point to real source material and supervisor feedback. The skills do not include
private annotated manuscripts or a preloaded literature database. Record work
that is excluded, deferred, or only planned so it cannot silently become a
demonstrated contribution.

For LaTeX, identify the true entry file, bibliography backend, engine, working
directory, and build command. For Word or Markdown manuscripts, simply name
those files; the writing, evidence, and presentation skills are format-neutral.
The LaTeX skill is optional and does not provide a university template.

## Share with a collaborator

Install project-local copies with `--project`, commit the skill folders, and
include a shareable brief. Keep private papers, data, comments, and credentials
out of the public skill repository. Each collaborator still needs their chosen
assistant, and only PDF conversion needs the optional Marker dependencies.

Personal preferences can remain in the collaborator's own assistant settings.
Project instructions and explicit task scope take precedence over the generic
guidance. An outline request does not authorize a wholesale manuscript rewrite.
