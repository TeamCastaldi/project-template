# Contributing

Thanks for your interest in contributing to this template. This document covers the expected workflow.

## Workflow

No issue required. If you spot something wrong or missing, go straight to a branch.

### 1. Branch

Use the branch-workflow prompt (`.github/prompts/branch-workflow.prompt.md`) or follow the naming convention directly:

```
feature/short-description
fix/short-description
docs/short-description
refactor/short-description
test/short-description
experiment/short-description
```

Branch names are snake_case. Keep them short and descriptive.

### 2. Make your changes

Work atomically — one logical change per commit. Use the `session-manager` skill's `/commit-msg` mode (`.claude/skills/session-manager/`) or follow Conventional Commits format directly:

```
feat(scope): add sync-template prompt
fix(ci): correct ruff check command
docs(readme): update quick start steps
refactor(db): simplify migrations readme
```

Conventional Commits format is **expected**, not optional.

### 3. Open a PR

CI must be green. The template ships no app code, but it does ship the scripts its skills depend on, and [`.github/workflows/skills-ci.yml`](.github/workflows/skills-ci.yml) lints and tests them. Run the same checks locally before pushing:

```bash
python3 -m pip install -r requirements-dev.txt   # pinned — same versions CI uses
bash scripts/validate_skills.sh                  # skill layout and frontmatter
bash scripts/check_doc_claims.sh                 # docs vs. what the repo contains
bash scripts/test_check_doc_claims.sh
bash scripts/test_check_scaffolded_project.sh
bash .claude/skills/init-project/scripts/test_check_inherited_docs.sh
bash .claude/skills/sync-from-template/scripts/test_compare_template.sh
ruff check .claude/skills
python3 -m pytest .claude/skills/dependabot/scripts -q
```

If you changed anything a scaffolded project inherits — a doc, a workflow, a prompt Config block — run the scaffold smoke test too. It is the only check that exercises scaffolding end to end, and it catches template-only content leaking into files that travel downstream:

```bash
bash scripts/simulate_init.sh python-cli /tmp/scaffold-check
bash scripts/check_scaffolded_project.sh /tmp/scaffold-check
```

Install from `requirements-dev.txt` rather than a bare `pip install ruff`. The pins there are what CI enforces, and a newer ruff enables rules CI does not — that difference is a green local run and a red PR.

No other minimum bar — this is a solo-maintained template repo. Fill in the PR template.

### 4. Merge

Squash or merge commit, your call.

---

## Keeping the template in sync

When you change the folder structure, add a prompt, or update a tooling default — run the sync-template prompt (`.github/prompts/sync-template.prompt.md`) to check for drift between the structure and its documentation. Your future self will thank you.

## What's in scope

- Improvements to the folder structure or READMEs
- New or improved prompts in `.github/prompts/`
- New or improved skills in `.claude/skills/` — see [`.claude/skills/README.md`](.claude/skills/README.md) for what earns a slot there
- CI, dependabot, or tooling updates
- Bug fixes in any template file

## What's out of scope

- Application code or a hardcoded stack (this is a stack-agnostic template — stack choice happens per-project via the `init-project` skill, not in the template itself)
- Skills tied to one person's infrastructure or non-engineering workflows — every cloned project inherits `.claude/skills/`, so a homelab or personal skill becomes dead weight in repos that have nothing to do with it
