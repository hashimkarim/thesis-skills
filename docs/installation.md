# Installation and updates

Use the Python installer for either assistant, or the Claude Code plugin for
Claude. Both methods load the same `skills/` content. Installing a skill adds
instructions and helpers; it does not execute the PDF converter or change your
manuscript, agent configuration, shell profile, or Python environment.

## Python installer

Requires Python 3.10+; no pip packages, administrator privileges, or symbolic
links. Clone or download this repository, then run from its root:

```bash
python3 install.py --agent both --dry-run
python3 install.py --agent both
```

Use `py -3` on Windows or `python` if that is your Python 3.10+ executable.
The script may also be called by its quoted full path from another directory.

| Scope | Codex | Claude Code |
| --- | --- | --- |
| Personal, default | `~/.agents/skills/` | `~/.claude/skills/` |
| Project, `--project PATH` | `PATH/.agents/skills/` | `PATH/.claude/skills/` |
| Explicit location | `--codex-dir PATH` | `--claude-dir PATH` |

Claude's personal location respects `CLAUDE_CONFIG_DIR` when set. Codex uses the
current `.agents/skills` convention, not an implicit `CODEX_HOME` override. To
target an older/custom Codex installation explicitly:

```bash
python3 install.py --agent codex --codex-dir "${CODEX_HOME:-$HOME/.codex}/skills"
```

That example uses Bash syntax; in PowerShell pass the actual directory or use
`--codex-dir "$env:USERPROFILE/.codex/skills"`. Avoid installing the same named
skill into multiple locations your host scans.

These defaults follow the official [Codex local skill locations](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code skill locations](https://code.claude.com/docs/en/skills).

### Project-local or selected skills

The project must already exist. Installing into it creates only skill directories:

```bash
python3 install.py --project "../my-thesis" --agent both
python3 install.py --agent codex --skill thesis-writing --skill thesis-citations
python3 install.py --list
```

`--skill` is repeatable; leaving it out selects all seven. Individual skills are
self-contained, including their references, scripts, and license. No sibling
skill must be installed. Copies contain no links back to this checkout.

### Update and resolve conflicts

Update your checkout using your normal Git workflow, then rerun the same install
command with the same target and scope. For a clean ordinary clone:

```bash
git pull --ff-only
python3 install.py --agent both
```

Unchanged installations are left alone. Unmodified managed installs can be
updated automatically. A content receipt identifies files owned by the installer;
local edits or a pre-existing skill cause a refusal before any planned changes.

To replace conflicts deliberately, add `--force`. Updates and replacements save
the previous folder outside the active skills directory, at:

```text
<parent of skills directory>/.thesis-skills-backups/<timestamp-id>/<skill-name>/
```

The printed path identifies each backup. Keep custom project preferences in
`THESIS.md` to make future skill updates easier. If customizing skills themselves,
maintain a fork or compare a backup with the new version before discarding it.

Each skill replacement is staged and restored if its final rename fails. The
operation is not a transaction across every skill: an OS error partway through
may leave earlier skills successfully updated. Rerunning is safe; inspect the
reported paths if an OS-level error occurs.

### Uninstall

Use the same agent, project, or custom-directory options as installation:

```bash
python3 install.py --agent both --uninstall --dry-run
python3 install.py --agent both --uninstall
python3 install.py --project "../my-thesis" --agent codex --uninstall
```

Only installs with a valid package receipt are removed. Unrelated skills are
preserved. Local edits block removal; `--uninstall --force` moves edited managed
skills to backup. Even `--force` refuses to uninstall an unmanaged skill.
Backups and your project brief remain until you choose to remove them.

## Claude Code plugin

```bash
claude plugin marketplace add hashimkarim/thesis-skills
claude plugin install thesis-skills@thesis-skills
```

Start a new session if necessary, then use `/thesis-skills:thesis-writing` or
another skill's namespaced command. You can also add the marketplace and install
through Claude's `/plugin` interface. This follows the official
[marketplace workflow](https://code.claude.com/docs/en/plugin-marketplaces).

For local development, `claude --plugin-dir .` loads this checkout. To check its
metadata without installing, run `claude plugin validate .`.

Manage updates or uninstall with Claude's `/plugin` interface. For reproducible
team snapshots or environments that only load repository skills, use the
project-local Python installer instead. Do not also install copied Claude
skills unless you intentionally want both plain and namespaced entries.

## Troubleshooting

- **Skill does not appear:** verify the printed location, start a new session,
  and check that the host is reading that project or personal skills directory.
- **Existing skill conflict:** inspect your local version; use `--force` only
  when replacement with a backup is intended.
- **Permission denied:** choose a user-writable directory or fix ownership. No
  part of the installer needs to run as administrator.
- **PDF conversion fails:** skill installation and Marker availability are
  separate. See [PDF conversion](pdf-conversion.md).
- **Desktop/web Claude differs:** this package targets Claude Code's filesystem
  and plugin interfaces. A copied personal skill does not automatically install
  into a hosted account. Use that product's supported import workflow separately.
