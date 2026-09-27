# Changelog

Notable changes to this template. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The current version is in [`.template-version`](.template-version). A project scaffolded from this template carries a copy of that file recording the version it was scaffolded from, so `sync-from-template` can report how far behind it has fallen and which entries below it missed.

## What the version numbers mean here

This template ships structure and workflows, not a library API, so SemVer is read against a *downstream project* rather than a compiler:

- **Major** — a change a downstream project must act on by hand. A folder or file it is expected to have moves or is removed; a command or skill changes its contract; a convention changes in a way that makes existing project files wrong.
- **Minor** — new capability that costs a downstream project nothing to adopt. A new command, skill, workflow, or doc section.
- **Patch** — fixes and clarifications. Corrected docs, bug fixes in a script, wording.

## Migration steps convention

A **Major** entry that requires action gets its own `### Migration steps` heading — a sibling of `### Added` / `### Changed`, not nested under other prose — holding a flat bullet list, one action per line, each starting with a verb `sync-from-template` recognizes:

- `DELETE <path>` — remove this path if it exists. Idempotent: a repo that already lacks it needs nothing done.
- `EDIT <path>: <what "done" looks like>` — describe the target state to check for and bring about, not a diff. When the exact content already lives in the template's own copy of `<path>` (its `CLAUDE.md`, say), point at that instead of repeating it here — a second copy is one more place for the two to drift.

Every action names a full path, verbatim, so the skill can act without guessing, and never touches a path this list doesn't name.

List only what the skill's normal add/update sync cannot do on its own: deletions, and edits to files outside `.claude/`. A file merely added or changed under `.claude/` needs no entry — the regular sync already offers it the moment it sees `NEW` or `CHANGED`.

A Major entry with no `### Migration steps` block is still shown to whoever runs the sync, as text to read and act on by hand — it is never guessed at.

## [Unreleased]

## [2.1.0] - 2026-09-27

Pulled forward what two real projects' test-suite audits (one on a Python/pytest backend, one on a Python MCP server) converged on independently: the same handful of mock-and-fake mistakes and the same missing-coverage patterns kept showing up. Written up once here instead of being rediscovered per project.

### Added

- `.claude/skills/testing-standards/` — a stack-agnostic skill applied whenever writing or reviewing a test, in any language or runner. Encodes Khorikov's four properties of a good test, a mock/fake table (what an outgoing call, an incoming stub, your own state, and your own internal function may each be asserted against — plus a new **F1** rule that a fake must be no more forgiving than the real dependency it replaces), the no-tautology/no-duplicate/don't-test-the-framework rules, and four recurring smells found in real audits (lenient fakes, weak `"error" in result`-style checks, read tools tested only on their empty case, and settings that are never proven to be wired up).
- `.claude/commands/audit-tests.md` (`/audit-tests`) — the occasional, deliberate full-suite audit this skill's rules feed into: a file-by-file review against a fixed, machine-validated JSON schema, a coverage-based redundancy shortlist, and mutation-testing spot checks (with a per-stack tool table and a documented workaround for mutation tools that refuse to run against a project's real layout). Writes a dated `docs/audits/YYYY-MM-DD-test-suite/` folder; self-provisions that folder's README on first use rather than shipping an empty stub in every clone.
- `.claude/skills/testing-standards/scripts/validate_test_audit.py` (with its own test suite) — validates an audit's `files.json` against the schema: required keys, allowed verdicts and rule codes, that a file's verdict actually follows from its findings, and that `is_redundant` matches its redundancy findings. Takes an optional `--tests-file` (a plain `<file>\t<test id>` list any stack's runner can produce) to also check that every named test really exists and, with `--complete`, that every test file has an entry — but runs schema-only validation with neither, so it's useful before a project has wired up that collection step.

### Changed

- `.github/workflows/skills-ci.yml` and `CONTRIBUTING.md`'s local-check list now run `pytest` over all of `.claude/skills`, not just the dependabot skill's scripts, so a new skill's tests are picked up without a further CI edit. A project that already synced an older `.claude/` and wants this: change the `python -m pytest .claude/skills/dependabot/scripts -q` line in its own `.github/workflows/skills-ci.yml` (and the matching line in `CONTRIBUTING.md`) to `python -m pytest .claude/skills -q`.

## [2.0.0] - 2026-09-19

One mechanism per job. Reusable workflows lived in three places — `.github/prompts/`, `.claude/skills/`, and a skill with slash commands hand-rolled inside it — with no rule saying which to use. They now live in two, with a rule.

### Migration for existing projects

A project scaffolded from 1.x must act on this by hand. `/sync-from-template` reads the list below and proposes these actions itself; they're spelled out here for anyone applying them without it.

Pulling `.claude/commands/` in isn't listed below — that's what the skill's normal sync already offers, the moment it sees those files as `NEW`.

### Migration steps

- `DELETE .github/prompts/` — nothing reads it any more; its two workflows are now `.claude/commands/branch-workflow.md` and `.claude/commands/sync-template.md`.
- `DELETE .claude/skills/session-manager/` — its three modes are now `/session-start`, `/session-end`, `/commit-msg`.
- `EDIT CLAUDE.md: has a "## Session Config" table holding TEST_COMMAND, LINT_COMMAND, SRC_ROOT, DOCS_ROOT, ADR_PATH and SNAPSHOT_PATH.` Copy the table verbatim from the template's own `CLAUDE.md` if this project's copy doesn't have one yet.

The slash commands keep the names they already had, so nothing you type changes: `/session-start`, `/session-end`, `/commit-msg`, plus `/branch-workflow` and `/sync-template` which were previously attach-a-file prompts.

### Changed

- **`.github/prompts/` is gone.** It existed for GitHub Copilot's attach-a-file behavior. `branch-workflow.prompt.md` and `sync-template.prompt.md` became `.claude/commands/branch-workflow.md` and `.claude/commands/sync-template.md`, which need no attaching. <!-- inherited-docs-ok -->

- **The `session-manager` skill split into three commands.** It was 322 lines containing a "Mode selection" table routing `/session-start`, `/session-end` and `/commit-msg` to different phases — a dispatcher written by hand because skills cannot be invoked by name. Splitting it also ends a trigger collision with a near-identical marketplace skill, since an explicitly invoked command never competes for phrasing.
- **Config consolidated into `CLAUDE.md`'s `## Session Config`.** Two competing homes existed: prompt files carried their own `## Config` blocks while `session-manager` already read a `## Session Config` section from `CLAUDE.md`. Splitting into five command files would have made that duplication worse, so there is now one table and every command reads it.

### Added

- `.claude/README.md` — the rule deciding hook versus skill versus command, the signs you chose wrong, and a "Workflows that moved" table so an old reference still leads somewhere.
- `.claude/hooks/session-start-hook.sh` and a `settings.json` wiring it to `SessionStart`. It answers one question as a session opens — can this session run the tests? — by reading `TEST_COMMAND` from `## Session Config` rather than guessing the stack. It never installs, never fails a session, and says nothing when all is well, because a hook cannot be declined and one that cries wolf is one nobody reads.
- A naming convention for hooks, `hooks/<event>-hook.sh`, plus five standing rules every hook follows. The suffix disambiguates the `/session-start` command from the `SessionStart` hook, which do unrelated jobs.
- `.claude/settings.local.json` is now gitignored. It was not, so a personal permission grant would have been committed into the shared repo.
- A `permissions` block in `settings.json`: `deny` on reads of secret-bearing files, `ask` on destructive git operations, and an `allow` list covering only the read-only checks this repo ships. The three lists are not symmetric — deny only removes capability, while allow is a grant made on behalf of every downstream clone — so deny is generous and allow is narrow. `.env.example` is deliberately readable, and `simulate_init.sh` is deliberately not allowlisted since it writes a caller-named tree.
- `check_doc_claims.sh` now also verifies every `Bash(bash …)` allow rule names a script that exists. A rule pointing at a renamed file grants nothing while still reading like a grant. Matcher *behavior* remains unverifiable from a script, which is why the permissions are documented as a seatbelt rather than a vault.

### Fixed

- `simulate_init.sh` listed only tracked files, so a file written but not yet `git add`ed was silently absent from every simulation — precisely the file most likely to be wrong. It produced a green local run and a red CI one for the same commit. Now lists what git would commit (`--cached --others --exclude-standard`).

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
