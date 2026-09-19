# Changelog

Notable changes to this template. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The current version is in [`.template-version`](.template-version). A project scaffolded from this template carries a copy of that file recording the version it was scaffolded from, so `sync-from-template` can report how far behind it has fallen and which entries below it missed.

## What the version numbers mean here

This template ships structure and workflows, not a library API, so SemVer is read against a *downstream project* rather than a compiler:

- **Major** — a change a downstream project must act on by hand. A folder or file it is expected to have moves or is removed; a command or skill changes its contract; a convention changes in a way that makes existing project files wrong.
- **Minor** — new capability that costs a downstream project nothing to adopt. A new command, skill, workflow, or doc section.
- **Patch** — fixes and clarifications. Corrected docs, bug fixes in a script, wording.

## [Unreleased]

## [2.0.0] - 2026-09-19

One mechanism per job. Reusable workflows lived in three places — `.github/prompts/`, `.claude/skills/`, and a skill with slash commands hand-rolled inside it — with no rule saying which to use. They now live in two, with a rule.

### Migration for existing projects

A project scaffolded from 1.x must act on this by hand:

1. Delete `.github/prompts/`. Nothing reads it any more.
2. Copy `.claude/commands/` from the template, or run `/sync-from-template`, which now syncs `.claude` alone.
3. Delete `.claude/skills/session-manager/`, whose three modes are now three commands.
4. Add a `## Session Config` table to `CLAUDE.md` holding `TEST_COMMAND`, `LINT_COMMAND`, `SRC_ROOT`, `DOCS_ROOT`, `ADR_PATH` and `SNAPSHOT_PATH`. The commands read these from there instead of from per-file Config blocks.

The slash commands keep the names they already had, so nothing you type changes: `/session-start`, `/session-end`, `/commit-msg`, plus `/branch-workflow` and `/sync-template` which were previously attach-a-file prompts.

### Changed

- **`.github/prompts/` is gone.** It existed for GitHub Copilot's attach-a-file behavior. `branch-workflow.prompt.md` and `sync-template.prompt.md` became `.claude/commands/branch-workflow.md` and `.claude/commands/sync-template.md`, which need no attaching. <!-- inherited-docs-ok -->

- **The `session-manager` skill split into three commands.** It was 322 lines containing a "Mode selection" table routing `/session-start`, `/session-end` and `/commit-msg` to different phases — a dispatcher written by hand because skills cannot be invoked by name. Splitting it also ends a trigger collision with a near-identical marketplace skill, since an explicitly invoked command never competes for phrasing.
- **Config consolidated into `CLAUDE.md`'s `## Session Config`.** Two competing homes existed: prompt files carried their own `## Config` blocks while `session-manager` already read a `## Session Config` section from `CLAUDE.md`. Splitting into five command files would have made that duplication worse, so there is now one table and every command reads it.

### Added

- `.claude/README.md` — the rule deciding skill versus command, the signs you chose wrong, and a "Workflows that moved" table so an old reference still leads somewhere.

## [1.1.0] - 2026-09-19

Scaffolding is now verified end to end, and documentation claims are checked against the repo rather than trusted.

### Added

- `scripts/check_scaffolded_project.sh` — asserts every post-condition `init-project` promises: no surviving placeholders, no empty section where a placeholder was removed, `docs/foundation.md` written, ADR files indexed and linked from `CLAUDE.md`, and no template-only file carried into the project. Useful on a real project, not only in CI; `init-project` Phase 7 now gates on it.
- `scripts/simulate_init.sh` and `.github/workflows/template-ci.yml` — take a fresh copy through the transformations the phases describe, for a Python CLI and a TypeScript web app, then verify the result. Also asserts the verifier *rejects* an un-initialized repo, since a check that passes on everything checks nothing.
- `scripts/check_doc_claims.sh` — resolves ecosystems, manifest filenames, and script paths named in the root docs against `.github/dependabot.yml` and the files on disk. This is the gap `check_inherited_docs.sh` names in its own header and cannot close.
- Test suites for both new scripts, 33 cases in total.

### Fixed

- `SECURITY.md` claimed Dependabot watched `npm`, which was never configured, and pointed at a `requirements.txt` that does not exist. Both are now correct, and `check_doc_claims.sh` keeps them that way.
- `.github/workflows/skills-ci.yml` described itself as testing "this template", so every scaffolded project inherited a workflow asserting it was the template. Found by the new scaffold smoke test on its first run.
- Template-only CI moved out of `skills-ci.yml` into `template-ci.yml`. Its negative test asserts this repo fails scaffolding verification — true in the template, false in a scaffolded project, where it would have turned CI red on correct initialization.

## [1.0.0] - 2026-09-19

First versioned release. Everything before this point is unversioned history; `1.0.0` marks the template as it stood once it carried a version, a changelog, and CI over its own tooling.

### Added

- `.template-version` and this changelog, so a scaffolded project can tell which template state it came from and what has changed since.
- `.github/workflows/skills-ci.yml` — shellcheck, skill-layout validation, and tests for every script the template's skills call. The template previously shipped 450+ lines of script with nothing running them.
- `scripts/validate_skills.sh` — checks each skill directory for a correctly named `SKILL.md`, valid frontmatter, a `name` matching its directory, and no stray packaged `.skill` archives.
- Test suites for the shipped scripts: `test_check_inherited_docs.sh` (16 cases), `test_compare_template.sh`, and `test_categorize_prs.py` (34 cases).
- `.claude/skills/README.md` — what earns a slot in a template-wide skills folder, and the layout rules a skill must follow to load at all.
- `TEMPLATE_VERSION` in `compare_template.sh` output, so the sync workflow can report a version gap rather than only a file-by-file diff.
- `requirements-dev.txt`, pinning the lint and test tooling CI installs, plus a Dependabot `pip` block watching it. The first CI run proved why: an unpinned `ruff` picked up a newly default-enabled rule and failed a build that had passed locally minutes earlier, on a PR that changed no Python.

### Changed

- ADRs are now the single home for architecture decisions: each gets its own file in `docs/ADRs/`, indexed in that folder's README, with `CLAUDE.md`'s Decision log holding links only rather than duplicating the content.
- `init-project` now recommends the Claude Code cloud environment settings (Network access, Environment variables, Setup script) as ready-to-paste blocks, derived from the stack it just scaffolded.
- `CONTRIBUTING.md` no longer claims there is nothing to lint or test at the template level — it names the checks CI runs and how to run them locally.

### Removed

- The `version-upgrade-planner` skill. It was specific to one person's home lab rather than to building software, its file was named `version-upgrade-planner-SKILL.md` so it never loaded, and a redundant packaged `.skill` archive sat beside it. The working copy lives in a marketplace, where a personal skill belongs.

[Unreleased]: https://github.com/TeamCastaldi/project-template/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/TeamCastaldi/project-template/releases/tag/v2.0.0
[1.1.0]: https://github.com/TeamCastaldi/project-template/releases/tag/v1.1.0
[1.0.0]: https://github.com/TeamCastaldi/project-template/releases/tag/v1.0.0
