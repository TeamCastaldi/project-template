# Changelog

Notable changes to this template. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The current version is in [`.template-version`](.template-version). A project scaffolded from this template carries a copy of that file recording the version it was scaffolded from, so `sync-from-template` can report how far behind it has fallen and which entries below it missed.

## What the version numbers mean here

This template ships structure and workflows, not a library API, so SemVer is read against a *downstream project* rather than a compiler:

- **Major** — a change a downstream project must act on by hand. A folder or file it is expected to have moves or is removed; a skill or prompt changes its contract; a convention changes in a way that makes existing project files wrong.
- **Minor** — new capability that costs a downstream project nothing to adopt. A new skill, prompt, workflow, or doc section.
- **Patch** — fixes and clarifications. Corrected docs, bug fixes in a script, wording.

## [Unreleased]

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

[Unreleased]: https://github.com/TeamCastaldi/project-template/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/TeamCastaldi/project-template/releases/tag/v1.0.0
