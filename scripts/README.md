# Scripts

Dev-time utilities that support development but are not part of the shipped product. Scripts here are tools for the developer, not the application.

## What belongs here

- Environment setup helpers
- Data import/export utilities
- Local development conveniences (reset DB, generate test data, etc.)
- Build or deployment helpers that don't belong in CI
- One-off migration or cleanup scripts (keep even after use — they document what was done)

## What does not belong here

- Application code (that goes in backend/)
- Test files (those go in tests/)
- CI/CD pipeline definitions (those go in .github/workflows/)

## What is already here

These ship with the repo and are run by CI. Each has a header block explaining its checks, output format, and exit codes.

| Script | Checks |
|---|---|
| `validate_skills.sh` | Every `.claude/skills/*/` has a correctly named `SKILL.md` with valid frontmatter, within the skill authoring guide's limits (name format, a description of at most 1,024 characters, a body of at most 500 lines), and no stray packaged `.skill` archive. Warns, without failing, when a body is long enough to lose its end after compaction |
| `check_doc_claims.sh` | Claims the root docs make — ecosystems, manifest filenames, script paths — resolve against what the repo actually contains |
| `check_scaffolded_project.sh` | A repo satisfies every post-condition `init-project` promises: no placeholders, `docs/foundation.md` present, ADRs indexed and linked, no template-only file or folder left behind (the template's `docs/template/` records, or a `SNAPSHOT_PATH` still pointing there) |
| `check_issues.sh` | The repo's open GitHub Issues, from `gh` or the GitHub connector as JSON: lists them in pick-up order and flags label and body problems (no status or type, two of either, planned with no priority, no acceptance criteria, all criteria ticked yet open, blocked with no reason). Run by the `issue-tracker` skill, `/roadmap` and `/session-start` |
| `sync_labels.sh` | Creates or updates the repo's GitHub labels to match `.github/labels.yml`; never deletes one. `--check` only reports. Run by `.github/workflows/label-sync.yml` on every push to `main`, and by the `issue-tracker` skill |
| `simulate_init.sh` | Not a check — builds an as-if-initialized fixture so CI can verify scaffolding end to end |

Each has a `test_*.sh` beside it. Run the tests before changing one; several of these checks look like they pass when they are silently doing nothing.

## Conventions

- Name scripts clearly: `reset-db.py`, `seed-dev-data.sh`, `export-users.ps1`
- Include a docstring or comment block at the top of each script explaining what it does, when to use it, and any required environment variables
- Cross-platform where possible — if a script is Windows-only or Linux-only, say so at the top
- Never hardcode secrets — read from environment variables or .env
