# {PROJECT_NAME}

{One or two sentence description of what this project does and who it's for.}

---

## Getting started

This is a stack-agnostic project template — it ships no app code, no framework choice, and no folder scaffolding. The first thing to do in a fresh repo cloned from this template is run the **init-project** skill (`.claude/skills/init-project/`):

1. Open Claude (or Copilot Chat) in this repo
2. Ask it to set up the project — the skill loads on its own, or invoke it by name
3. Answer the requirements-gathering interview — project purpose, target user, stack, architecture, constraints
4. Review and approve the scaffolding plan it proposes

That run scaffolds the folders this project actually needs (e.g. `backend/`, `frontend/`, `db/`, or none of those, depending on the answers), writes a README into each, fills in `CLAUDE.md`, and writes `docs/foundation.md`. It also re-points the docs this template ships — `CONTRIBUTING.md`, `SECURITY.md`, and the rest — so they describe your project rather than the template. This README's own Stack, Quick Start, and Project Structure sections below get filled in as part of that.

Once that's done, delete this "Getting started" section.

### Staying current with the template

`.template-version` records which template version this repo was scaffolded from — leave it in place. The **sync-from-template** skill reads it to report how far behind the project has fallen and which [`CHANGELOG.md`](CHANGELOG.md) entries it missed, rather than just diffing every file blind.

## Stack

<!-- init-project fills this in -->

## Quick Start

<!-- init-project fills this in with the real setup steps for the chosen stack -->

## Project Structure

```
docs/           All project documentation
scripts/        Dev-time utilities (not shipped)
```

init-project adds to this list as it scaffolds folders (`backend/`, `frontend/`, `db/`, `tests/`, or others, as needed).

For architecture decisions, see `docs/ADRs/`.
For technical specs, see `docs/specs/`.
For SOPs and runbooks, see `docs/SOPs/`.
For the founding brief, see `docs/foundation.md`.
