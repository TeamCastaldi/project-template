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

Work atomically — one logical change per commit. Use the create-commit prompt (`.github/prompts/create-commit.prompt.md`) or follow Conventional Commits format directly:

```
feat(scope): add sync-template prompt
fix(ci): correct ruff check command
docs(readme): update quick start steps
refactor(db): simplify migrations readme
```

Conventional Commits format is **expected**, not optional.

### 3. Open a PR

CI must pass (ruff + pytest). No other minimum bar — this is a solo-maintained template repo. Fill in the PR template.

### 4. Merge

Squash or merge commit, your call.

---

## Keeping the template in sync

When you change the folder structure, add a prompt, or update a tooling default — run the sync-template prompt (`.github/prompts/sync-template.prompt.md`) to check for drift between the structure and its documentation. Your future self will thank you.

## What's in scope

- Improvements to the folder structure or READMEs
- New or improved prompts in `.github/prompts/`
- CI, dependabot, or tooling updates
- Bug fixes in any template file

## What's out of scope

- Application code (this is a template, not an app)
- Stack changes without discussion (e.g. switching from FastAPI to Django)
