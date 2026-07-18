# {PROJECT_NAME}

{One or two sentence description of what this project does and who it's for.}

---

## Getting started

This is a stack-agnostic project template — it ships no app code, no framework choice, and no folder scaffolding. The first thing to do in a fresh repo cloned from this template is run the **init-project** prompt (`.github/prompts/init-project.prompt.md`):

1. Open Copilot Chat (or Claude) in this repo
2. Attach `.github/prompts/init-project.prompt.md` and follow its instructions
3. Answer the requirements-gathering interview — project purpose, target user, stack, architecture, constraints
4. Review and approve the scaffolding plan it proposes

That run scaffolds the folders this project actually needs (e.g. `backend/`, `frontend/`, `db/`, or none of those, depending on the answers), writes a README into each, fills in `CLAUDE.md`, and writes `docs/foundation.md`. This README's own Stack, Quick Start, and Project Structure sections below get filled in as part of that.

Once that's done, delete this "Getting started" section.

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
