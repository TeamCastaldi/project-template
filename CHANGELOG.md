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

The next release is **Major (3.0.0)**: six commands no longer start on their own (see the first entry under Changed). Most of the rest came from the skill best-practices review in `docs/template/`; the issue tracking on GitHub Issues replaced a file-based `/roadmap` that never shipped in a release. Edits that fall outside what `/sync-from-template` copies are listed under Migration steps at the end of this section.

### Added

- **Issue tracking on GitHub Issues**, usable from plain conversation and ready in a new repo with no setup. Planned work, bugs, tech debt and ideas live as issues with one `status:*` label (`backlog`, `planned`, `in-progress`, `blocked`), one `type:*` label (`feature`, `improvement`, `bug`, `debt`, `idea`) and, once triaged, one priority (`p0:critical` to `p3:low`). Closing an issue is what marks it done; there is no completed status. `docs/SOPs/SOP-issue-tracking.md` is the how-to, and `docs/template/issues-roadmap-plan.md` records the decisions.
  - The `issue-tracker` skill files, finds, starts, blocks and closes issues when the user talks about them: "note that export breaks on Safari, we'll fix it later" becomes a drafted issue, filed on a plain yes, with anything not said marked `_Not yet known_` rather than invented. A skill and not a command because it should run whenever issues come up, even for someone who never learned it exists.
  - `.github/labels.yml` defines the labels, and `scripts/sync_labels.sh` (22 test cases) makes GitHub match it, creating and updating but never deleting. `.github/workflows/label-sync.yml` runs it on every push to `main`, so a repo gets its labels on its first push; `workflow_dispatch` lets a cloud session, whose GitHub connector cannot create labels, run it instead.
  - Five issue forms in `.github/ISSUE_TEMPLATE/` — feature, improvement, bug, tech debt, idea — each applying its type label and `status:backlog`, and asking for Context, a user story, acceptance criteria and dependencies as the type needs. Blank issues are off.
  - Every call goes through `gh api` to the REST API. `gh issue …` and `gh label …` use GraphQL, which Claude Code cloud sessions refuse; REST works there, locally and in Actions.
  - `scripts/check_issues.sh` (36 test cases) reads the open issues as JSON from `gh api` or the GitHub connector, skipping the pull requests the REST endpoint also returns, lists them in pick-up order, and flags label and section problems: no status or type, two of either, planned work with no priority or no acceptance criteria, an open issue with every criterion ticked, a blocked issue that does not say what it waits on.
- `/roadmap` — the deliberate, whole-backlog jobs on top of the issues: `seed` files an issue for each goal stated in `docs/foundation.md`, `CLAUDE.md` and the other planning docs, each citing its source; `evaluate` audits the open issues against the code and reports stated goals with no issue, without filing them; `migrate` turns a checklist `ROADMAP.md` from a pre-release version of this command into issues. Its guardrail is grounding — every issue cites a repo path, an existing issue or an explicit request — and every write sits behind an exact gate phrase.
- A command, skill and hook index in `.claude/README.md`. `/sync-template` already audited against one, and there was none.
- `.claude/skills/sync-from-template/tooling_paths.txt` — the files outside `.claude/` that its commands and skills run or depend on: `check_doc_claims.sh`, `check_scaffolded_project.sh`, `validate_skills.sh`, `check_issues.sh`, `sync_labels.sh` and their tests, plus `.github/labels.yml`, `.github/ISSUE_TEMPLATE/` and `.github/workflows/label-sync.yml`. `sync-from-template` now offers them alongside `.claude/`, so a synced project gets the issue tracking whole, not a skill without the labels it needs. A listed directory brings every file in it. The list is read from the template, so a new dependency is one line upstream and no downstream config changes. Anything unlisted stays untouched — `scripts/` also holds `simulate_init.sh`, which `init-project` removes on purpose and a whole-folder sync would keep re-offering.
- `docs/template/` — a folder for the template's own records: the session snapshots written while working on it, and reviews or plans about how it should change (`blueprint-review.md`, an assessment of another project's tooling, is the first). This repo's `SNAPSHOT_PATH` points at it, so `/session-end` writes there, and the two existing snapshots moved in with `git mv`. `init-project` deletes the whole folder when it scaffolds a project and resets `SNAPSHOT_PATH` to `docs/session-history/`. It is a folder and not a list of file names because the template adds a snapshot every session, so no list could stay current.
- `check_scaffolded_project.sh` reports `docs/template/`, and a `SNAPSHOT_PATH` still pointing into it, as `TEMPLATE_RESIDUE`. A project's own snapshots in `docs/session-history/` are never residue, and a test guards that. Six new cases, mutation-checked.
- Three evaluations per skill, in `.claude/skills/<name>/evals/evals.json` (skill-creator's format): a request each skill should trigger on, a near-miss that belongs to a neighbouring command or skill, and a behaviour it must get right. Script tests could only prove the scripts work; these check whether Claude picks the right skill and follows it. They need a model, so CI does not run them — `.claude/skills/README.md` now says how to run them and what setup each case needs. Projects receive them on sync and pay no context for them unless they are run; a project that deletes them is offered them again on the next sync. Run output (`.claude/skills/*-workspace/`) is gitignored.
- `validate_skills.sh` enforces the limits from Anthropic's skill authoring guide, which claude.ai uploads and the Skills API apply: `NAME_FORMAT` (1–64 lowercase letters, digits and hyphens), `NAME_RESERVED` (no "anthropic" or "claude"), `DESC_TOO_LONG` (over 1,024 characters), `XML_IN_FRONTMATTER` and `BODY_TOO_LONG` (over 500 lines). It now reads a folded or literal description whole, strips quotes and counts characters, not bytes; it previously read only a folded description's first line, which is why two descriptions over the limit passed CI. A `WARN` line, not counted as a problem, flags a body over 20,000 characters, roughly the part Claude Code keeps after compaction. The summary line gains `WARNINGS=<n>`. `scripts/test_validate_skills.sh` (33 cases) covers every check and is synced alongside the script. **A downstream project can newly fail this check** if one of its own skills breaks a limit; the output names the skill and the measured value, and the fix is to shorten the description or move body detail into files the skill links.
- A "Writing a skill" section in `.claude/skills/README.md`: the rules this repo now holds its own skills to, each pointing at the check or skill that shows it. They cover the size limits `validate_skills.sh` enforces, descriptions that say what and when, a body that holds only what Claude needs to act, must-not-lose instructions and progress checklists at the top, detail in files one level deep, scripts named by repo-relative path, and three evaluations per skill. It links Anthropic's skill authoring guide as the reference.
- `/legacy-cleanup` — audits the files or directories you name for dead code, obsolete feature flags and circular dependencies, and recommends removals with the exact `path:line` and symbol for each. Analysis only: it edits nothing, and it never recommends removing code a reflection, dynamic import or string lookup could reach. A command, not a skill, because a deep audit should start when someone chooses it; `disable-model-invocation` keeps Claude from starting it on its own, so it costs no context until run.

### Changed

- **Breaking for downstream projects.** Six commands, `/audit-tests`, `/branch-workflow`, `/roadmap`, `/session-end`, `/session-start` and `/sync-template`, now set `disable-model-invocation: true`, so only the user can start them. `.claude/README.md` already said a command is "decided by you"; until now Claude could start any of them on its own, and their descriptions sat in every session's context. Claude now suggests typing the command instead of running it. `/commit-msg` stays startable by Claude, because `/session-end` has Claude run it to draft the commit message. Every file involved is under `.claude/`, so `/sync-from-template` delivers the change and no migration step is needed. A project that wants Claude to keep starting one of these commands can delete that line from its copy.
- `dependabot` and `sync-from-template` lost text Claude only read after it had already picked the skill, or that was written for maintainers: `dependabot`'s "Edge cases" list restated a rule each phase already states, so it is gone (the one rule with no home in its phase, reporting the exact `gh` error when `gh pr create` or `gh pr merge` fails, moved into Phase 6), and its "Bundled script" note became two lines in Phase 2. `sync-from-template`'s "When to use this" restated the description and is now the one sentence that separates it from `/sync-template`; a note about what `init-project` might do "later" is gone, and the reasoning for an ephemeral clone moved into `compare_template.sh`'s header. `dependabot` gained a copyable progress checklist with its confirmation gate marked. Net, the two files are about 2,600 bytes smaller.
- `init-project` keeps its closing gate within the part of a skill Claude Code keeps after compaction (the first 5,000 tokens, roughly 20,000 characters). Its `SKILL.md` went from 28,867 to about 18,800 characters: Phase 4, the cloud environment settings and the `foundation.md` template moved, word for word, into `references/` files the skill reads when it reaches them, and a progress checklist at the top ends with the `check_scaffolded_project.sh` gate. The Phase 0 retrofit now loads only Phase 4's file. Why `init-project` owns the first docs pass moved to `.claude/README.md`, and stale names ("workflow prompts", "the template-sync workflow … once those exist") now name `/sync-template` and `/session-start`.
- `init-project` and `sync-from-template` have shorter descriptions: 796 and 687 characters, down from 1,307 and 1,302. Both were over the 1,024-character limit that claude.ai uploads and the Skills API apply. Claude Code shows up to 1,536, so nothing broke here, but every session's skill listing paid for the extra text. Every trigger phrase is kept; what went was implementation detail that belongs in the body, and `sync-from-template` listing its own `/name` as a trigger. `sync-from-template` and `docs-updater` now say "the user" rather than "Nathan", as the other skills already did.
- `docs-updater` says what counts as evidence of a change. The user's own description does, for the fact that the change happened, but not for details it leaves out: those come from the code and git history. A detail a reader would act on, such as a command's syntax, is asked for rather than guessed or left as a placeholder, and a decision's reason that nobody gave is marked as not recorded. In its first evaluation run the skill treated "I added an `export` subcommand" as too thin to document, yet drafted an ADR from "we moved to Postgres".
- `check_inherited_docs.sh` skips `docs/template/` the way it skips `.claude/skills/`: those files are meant to talk about the template, and a copy that leaks into a project is reported as a folder by `check_scaffolded_project.sh` instead. Three new cases, including one that stops the skip from reaching the rest of `docs/`.
- `simulate_init.sh` and `init-project`'s Phase 3 delete the folder and reset `SNAPSHOT_PATH`. This happens in the scaffold phase only, so the retrofit path for an already-initialized project never touches its session history. `CONTRIBUTING.md` now says where the template's own records go.
- `compare_template.sh` accepts a single file as a sync path. It previously handed every path to cone-mode sparse checkout, which rejects a file outright (`fatal: … is not a directory`, exit 128). Directories still go to sparse checkout; files are written from the commit afterwards, keeping their executable bit.
- `/session-start` reads the open issues through `check_issues.sh` and offers in-progress, then planned, issues as the session's mission. Picking one moves it to `status:in-progress`; the PR that finishes it carries `Closes #N`, which `.github/PULL_REQUEST_TEMPLATE.md` now suggests.
- `init-project` keeps the issue tracking as shipped and, at wrap-up, checks the repo's labels and offers to create any that are missing, or says the label workflow will on the first push to `main`; then offers `/roadmap seed`. Its docs pass keeps `CONTRIBUTING.md`'s pointer to the issue-tracking SOP.
- `sync-from-template` has a step for a sync that brings issue tracking into a project that lacked it: it checks the labels and offers to create them. `test_compare_template.sh` covers a directory in `tooling_paths.txt`, which no case did before.
- `check_scaffolded_project.sh` reports a missing `.github/labels.yml`, `label-sync.yml`, `sync_labels.sh`, `check_issues.sh` or issue form as `MISSING_FILE`. **A downstream project can newly fail this check** if it never synced the issue tracking, or removed it; the fix is to sync it in, or to drop the check if the project tracks work elsewhere.
- `CONTRIBUTING.md` says planned work lives in GitHub Issues, and `docs/plans/README.md` no longer lists roadmaps among what goes there.

The first sync after upgrading runs the project's older `compare_template.sh`, which knows nothing of the list: it pulls the new script, and the skill then runs the comparison again so the tooling files are offered in the same session.

### Fixed

- `check_inherited_docs.sh` and `check_scaffolded_project.sh` now prune `node_modules/` from their doc sweeps, the same way they already skip `.claude/skills/`. Neither previously excluded it, so any downstream project with dependencies installed had every installed package's README scanned for template language and broken links — hundreds of false `TEMPLATE_LANGUAGE`/`BROKEN_LINK` hits from ordinary phrases like "template" or a relative link that only resolves inside that package.
- `check_doc_claims.sh`'s ecosystem-claim check now accepts single-quoted `package-ecosystem:` values in `dependabot.yml`, not just double-quoted ones — both are ordinary YAML. It also no longer aborts the entire script with no output when the extraction pipeline matches zero lines (a `dependabot.yml` using only single quotes, or configuring no ecosystems yet), which under `set -euo pipefail` previously killed the whole run before it could print anything, including its own summary line.
- Every project scaffolded from the template inherited the template's own session snapshots, `docs/session-history/SESSION_SNAPSHOT_2026-09-27.md` and `SESSION_SNAPSHOT_2026-09-28.md`. `init-project` removed only the changelog, the template CI workflow and `simulate_init.sh`, and nothing checked. A project initialized from this version no longer gets them. A project initialized earlier can delete those two files if it still has them; any other snapshot in its `docs/session-history/` is its own, so leave it. Nothing breaks if they stay, so this is a note and not a migration step.
- `dependabot` and `sync-from-template` now name their bundled scripts by repo-relative path (`.claude/skills/<skill>/scripts/…`), the way `init-project` and `/audit-tests` already did. The bare `scripts/categorize_prs.py` and `scripts/compare_template.sh` they gave resolved to the root `scripts/` folder when run from the repo root, so the first call failed (exit 2 and exit 127) until Claude went looking for the file. `sync-from-template` also no longer asks Claude to read its script before running it; the script's output is what the skill needs, and reading it is now only for when that output looks wrong.
- `.claude/README.md` said a dispatcher skill exists "only because skills cannot be invoked by name". Claude Code merged commands into skills, so any skill or command can be invoked by `/name`. The mechanism table now says who may start each one and which frontmatter field sets it (`disable-model-invocation`, `user-invocable`). This was K1 in `docs/template/blueprint-review.md`.
- The evaluation how-to in `.claude/skills/README.md` produced a flawed comparison. It had you commit the project; skill-creator then deleted the skill's files for the runs without it, and those runs found the files in git history. It now turns the skill off with `skillOverrides` in the project's `.claude/settings.local.json`, in a session of its own, and says to start Claude Code in the project being evaluated, with the commands to build and commit one.
- `docs-updater`'s case 1 could never pass: the project had no export code to document. It now runs after a fixture commit, `evals/files/export-command.patch`, that adds a real Click `export` command, and checks the documented syntax against it. Cases 2 and 3 scored the same with and without the skill although the outputs differed, so each gains a check for that difference: pointing the user to `/session-end` instead of writing the snapshot, and proposing edits instead of writing them.
- `check_doc_claims.sh` resolves a manifest named in a root doc at any depth. A monorepo whose `backend/requirements.txt` and `frontend/package.json` are named from `SECURITY.md` or `README.md` no longer fails with `MANIFEST_CLAIM`. A manifest that exists nowhere is still reported, and copies inside `.git`, `node_modules`, `.venv` or `.agents` do not count as the repo's own.
- `check_scaffolded_project.sh` accepts the founding brief at `docs/foundation/FOUNDING_BRIEF.md` as well as at `docs/foundation.md`, for a project that keeps its docs in a folder. A project with neither still reports `MISSING_FILE`.
- `check_inherited_docs.sh` skips `.venv/`, any other virtualenv (a folder holding a `pyvenv.cfg`) and `.agents/skills/`, as it already skips `node_modules/`. Those are installed or vendored third-party files, so their relative links were reported as `BROKEN_LINK` in an otherwise clean project.
- These three are Patch-level fixes, not a change to the Major contract. The two scripts `check_doc_claims.sh` and `check_scaffolded_project.sh` ship in the tooling `sync-from-template` copies, and `check_inherited_docs.sh` lives under `.claude/`, so a synced project gets them with no migration step.

### Migration steps

- `EDIT .gitignore: ignores .claude/skills/*-workspace/, where skill-creator writes evaluation runs.` Copy the block from the template's own `.gitignore`.
- `EDIT .github/workflows/skills-ci.yml: has a "Test validate_skills.sh" step running bash scripts/test_validate_skills.sh, after "Validate skill layout".` Copy the step from the template's own `skills-ci.yml`.
- `EDIT .github/workflows/skills-ci.yml: has "Test sync_labels.sh" and "Test check_issues.sh" steps running bash scripts/test_sync_labels.sh and bash scripts/test_check_issues.sh, and no step running test_check_roadmap.sh.` Copy the steps from the template's own `skills-ci.yml`.
- `DELETE scripts/check_roadmap.sh` — only in a project that synced from `main` while the file-based `/roadmap` was there; `/roadmap` now reads GitHub Issues through `check_issues.sh`.
- `DELETE scripts/test_check_roadmap.sh` — its test, for the same reason.
- `EDIT CLAUDE.md: ## Session Config has no ROADMAP_PATH row.` Only in a project that synced it in; nothing reads it now. If `docs/plans/ROADMAP.md` exists, run `/roadmap migrate` before removing the row, which turns the file into issues.

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
