# Blueprint review: what could improve this project template

Status: **proposal only. Nothing here has been adopted or changed.** Written 2026-10-04 against this repo at `main` (0d8aee6) and the public repo gitlab.com/macrodream/blueprint at commit `b272f45368a38f08a42a5d2f1cd5bd9bc9d5bca3`.

Citations: our files as `path:line`; blueprint's as `bp:path:line`. Line numbers will drift as files change. They were last re-checked against the repository after the template's own records moved into `docs/template/`, which is where this file lives: it is about the template, and `init-project` deletes that folder when it scaffolds a project (see `CONTRIBUTING.md`).

## Summary

Blueprint is a governance template for teams on GitLab and Claude Code. It is a useful mirror because it solves overlapping problems under different constraints: GitLab instead of GitHub, many contributors instead of one, and an application stack bolted on.

Of the 40 candidates considered, **14 are worth doing** (13 firmly, 1 optional), **5 are deferred** with a trigger for revisiting, and **21 are dropped** with a reason each. Nothing is a verbatim reuse: blueprint is Apache-2.0 and this repo is MIT, so every kept item is to be re-implemented in our own words.

The strongest findings are about **our own repo, not blueprint's features**. Blueprint mostly served as the prompt to test things we had never tested:

1. **Our docs state something the official docs contradict.** Two files say skills cannot be invoked by name; the skills docs say commands were merged into skills, and our root README already says to invoke one by name (K1).
2. **A hook can be silently disarmed.** Deleting the only line that wires our `SessionStart` hook left every check green (K2a).
3. **CI and the local check list disagree.** CI runs `shellcheck`; the contributor list never mentions it (K3).
4. **Our changelog links to tags that do not exist.** GitHub has no tags and no releases, and there is no link for 2.1.0 (K7).
5. **Our hook test cannot tell which output stream a message used**, though the stream decides whether Claude sees it (K6).

Blueprint's own descriptions of itself have drifted from its contents in three places (see "How far to trust blueprint"), so its self-reported figures are treated as unverified throughout.

## Findings worth doing, in suggested order

Effort is a rough guide (S under an hour, M a few hours, L a day or more). SemVer class follows the definitions in `CHANGELOG.md:9-13` as they apply to a project scaffolded from this repo.

### 1. K1: Correct the stale "skills cannot be invoked by name" premise

- **Class / effort / risk:** Patch / S / low (docs only).
- **Blueprint:** has no `commands/` folder at all. Its user-invoked workflows are skills marked `disable-model-invocation: true` (`bp:.claude/skills/mr/SKILL.md:4`, `bp:.claude/skills/release/SKILL.md:4`).
- **Our gap:** `.claude/README.md:69` says a skill's mode table "exists only because skills cannot be invoked by name", `.claude/README.md:7` and `.claude/skills/README.md:3` frame by-name invocation as what separates commands from skills, and `README.md:12` contradicts all three by telling the reader to invoke a skill by name.
- **Evidence:** Claude Code's skills documentation (fetched 2026-10-03 through a summarising tool, so re-read it before editing) says "Custom commands have been merged into skills", that `/skill-name` invokes any skill, that `disable-model-invocation: true` means you can invoke it and Claude cannot, and that `user-invocable: false` is the reverse. It contains no statement that skills cannot be invoked by name.
- **Proposed change:** fix the three passages, and describe the real axis (who may start it) with those two frontmatter fields in the mechanism table. Add a row for path-scoped rules (see K5). Keep the existing "who decides it runs" framework, which still holds.
- **Not implied:** migrating `commands/` to skills. Commands keep working, and that would be a Major change (see Deferred).

### 2. K2a: Verify that every hook is actually wired in

- **Class / effort / risk:** Minor / M / the check can newly fail a downstream project whose hook is unwired, which is its purpose. Match by filename so a differently written command path is not a false positive.
- **Blueprint:** a `load-bearing.declarations` file lists guards wired in by exactly one line, where deleting that line leaves the suite green, and a 600-line gate fails if one disappears (`bp:load-bearing.declarations:14`, `bp:scripts/check-load-bearing.sh:2`). Its own test is "delete the line and run the suite".
- **Experiment:** I ran that test on a scratch copy of this repo, removing the only `SessionStart` wiring from `.claude/settings.json` (line 48). All 8 gate scripts, `ruff`, and 62 `pytest` tests stayed green.
- **Why nothing noticed:** `scripts/check_doc_claims.sh:160-161` only checks that `allow` rules name scripts that exist. Our own changelog already names the class (the 2.1.0 entry in `CHANGELOG.md`: "settings that are never proven to be wired up").
- **Proposed change:** derive the check from our naming rule (`.claude/README.md:85`: a hook file is named for its event). For each `.claude/hooks/*-hook.sh`, assert `settings.json` wires it under that event. Add it to `check_doc_claims.sh`, with a regression test shown to fail against the unfixed script.
- **Not adopted:** blueprint's declarations file and gate, which are built for dozens of call sites where we have about one.

### 3. K2b: Stop registering a test script in four places by hand

- **Class / effort / risk:** Patch / M / **must not ship downstream.** Keep it out of `.claude/skills/sync-from-template/tooling_paths.txt` or gate it to this repo, because a scaffolded project's `CONTRIBUTING.md` is rewritten and would fail it.
- **Our gap:** the last roadmap session wired one new test script into `skills-ci.yml`, the `settings.json` allow rules, `scripts/README.md` and `CONTRIBUTING.md` by hand (`docs/template/SESSION_SNAPSHOT_2026-09-27.md:14`). Today all 6 test scripts are in both the CI file and the contributor list, so this is drift risk, not drift.
- **Blueprint:** "keep the pre-push set complete by derivation, not by hand" (`bp:scripts/CLAUDE.md:161`, `bp:CLAUDE.md:329`).
- **Proposed change:** a template-only check that every test script found on disk appears in `skills-ci.yml` and `CONTRIBUTING.md`.

### 4. K3: Add the missing `shellcheck` line to the contributor check list

- **Class / effort / risk:** Patch / S / none.
- **Our gap:** `.github/workflows/skills-ci.yml:34` runs `shellcheck` over every `.sh` file, but the local list (`CONTRIBUTING.md:51`) has no such line. `CONTRIBUTING.md:62` says the list exists so a local run matches CI, and a shell-lint failure is exactly the case where it does not. `shellcheck` was also not installed in the environment this review ran in.
- **Proposed change:** add the line, with how to install it.

### 5. K6: Teach hook authors which output stream an event reads

- **Class / effort / risk:** Patch / S to M / low. Re-read the hooks documentation when writing it.
- **Evidence:** Claude Code's hooks documentation (fetched 2026-10-03) says a `PreToolUse` block reason comes from stderr and plain stdout is ignored on exit 2; on exit 0, stdout reaches Claude only for `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart` and `PostModelSwitch`, and goes to the debug log otherwise.
- **Blueprint documents this itself, then breaks it** (`bp:CLAUDE.md:437`). `bp:.claude/hooks/pre-tool-safety.sh:28-29` prints its block reason to stdout and exits 2, and `bp:.claude/hooks/post-edit-checks.sh:97` prints its reminders to stdout on exit 0. By that documentation neither message reaches Claude, so both hooks do nothing as written.
- **Our gap:** our hook is correct today (`.claude/hooks/session-start-hook.sh:43` prints to stdout on `SessionStart`), but the hook rules (`.claude/README.md:93`) never say which stream an event reads, and the test merges both streams (`.claude/hooks/test_session-start-hook.sh:41`, `:57`), so a regression to stderr would stay green.
- **Proposed change:** add a per-event channel rule to the hook rules, and make the test capture stdout and stderr separately and assert the message is on stdout.

### 6. K5: Write down the rules for check scripts, as a path-scoped rule

- **Class / effort / risk:** Minor / M / how older Claude Code builds treat `.claude/rules/` is unverified, so check when implementing. Keep it short and written from our own incidents.
- **Evidence for the need:** the previous session's two bugs were exactly these rules. A zero-match extraction silently aborted `check_doc_claims.sh` under `set -euo pipefail`, and the first draft of its regression test passed vacuously (`docs/template/SESSION_SNAPSHOT_2026-09-28.md:4`, `:24`). Blueprint states the rules as "a gate must be able to fail" (`bp:scripts/CLAUDE.md:12`), "a self-test must tell a crash from a rejection" (`bp:scripts/CLAUDE.md:104`), and that `|| true` on a scan swallows the exit code that means the gate is broken (`bp:scripts/CLAUDE.md:46`).
- **Where it should live:** blueprint uses a nested `scripts/CLAUDE.md` because it believes Claude Code has no `paths:` loader (`bp:CLAUDE.md:285`). The memory documentation (fetched 2026-10-03) says it has: a `.claude/rules/*.md` file with a `paths:` field loads only when Claude works with matching files. That fits us better, because our check scripts live in three places (`scripts/`, `.claude/hooks/`, `.claude/skills/*/scripts/`) and a nested file would cover one. It also answers the standing-cost worry in `.claude/skills/README.md:3`, since a path-scoped rule costs a downstream project nothing until a matching file is touched.
- **Proposed change:** `.claude/rules/gate-scripts.md` with `paths:` for those three locations, plus a one-line pointer from `scripts/README.md`. Add it to the `.claude/README.md` index so `/sync-template` keeps checking it.

### 7. K13: Two missing smells in `testing-standards`

- **Class / effort / risk:** Patch / S / low.
- **Our gap:** `.claude/skills/testing-standards/SKILL.md:113` lists the recurring smells; neither "watch the test fail first (a negative control)" nor "a test file CI never collects, or a new file absent from the coverage report" is there. `/audit-tests` catches the first after the fact through mutation spot checks (`.claude/commands/audit-tests.md:122`), not at write time.
- **Blueprint:** `bp:tests/CLAUDE.md.example:20` and `:39`. Take only the portable six of its eight sections; two are browser and end-to-end specific.

### 8. K4: A `/adr` command

- **Class / effort / risk:** Minor / M / the body format must come from one place so it cannot drift from what `init-project` writes. It overlaps slightly with `docs-updater`.
- **Our gap:** we have the convention, an Index, a Decision log, and a checker that fails on an unindexed or unlinked ADR (`docs/ADRs/README.md`, `scripts/check_scaffolded_project.sh:187`, `:190`), but creating one is a manual edit in three places (`.claude/commands/branch-workflow.md:122`, `.claude/skills/docs-updater/SKILL.md:52`). Nothing creates it day to day.
- **Blueprint:** `bp:.claude/skills/adr/SKILL.md:13` numbers and writes the file, but does not maintain an index, so ours must do more. Its ADR README has one rule worth taking: no status for "accepted but not built"; use a dated Implementation-status blockquote under the status line instead (`bp:docs/adr/README.md:42`, `bp:.claude/skills/adr/SKILL.md:74`).
- **Cannot be copied:** blueprint numbers `0002-slug.md` with Proposed/Accepted statuses; we use `ADR-NNN-` and Accepted/Draft/Deprecated/Superseded.
- **Command, not skill:** by our own test (`.claude/README.md:65`) nobody needs an ADR created if they never learned the command exists.

### 9. K7: A release-state check, and a decision about tags

- **Class / effort / risk:** Patch / S to M / **template-only**: a downstream project's `.template-version` records which version it was scaffolded from, not its own.
- **Our gap:** `CHANGELOG.md` has a `[2.1.0]` section but no link reference for it among the references at the bottom of the file, and the `[Unreleased]` reference still compares from `v2.0.0`. **GitHub has no tags and no releases at all** (checked 2026-10-03 through the API), so the release links that do exist point at nothing. `.template-version` (`:1`, "2.1.0") is the only machine-read version, and `sync-from-template` reads it (`.claude/skills/sync-from-template/SKILL.md:22`).
- **Blueprint:** its lock-step gate would not fix this. By its own description its first rule is vacuous in a repo with one version file (`bp:scripts/check-version-lockstep.py:21`, `:25`).
- **Proposed change:** a small check that `.template-version` is not behind the newest released heading and that every released heading has a link reference. The data fix depends on **Decision A** below.

### 10. K10: `/session-end` should not push after a failed commit

- **Class / effort / risk:** Patch / S / none.
- **Our gap:** Step 4 is two commands on separate lines (`.claude/commands/session-end.md:63-64`), and the only failure handling in the file is for the test and lint gate (`:44`). Run as one script, the push runs after a failed commit. Not observed here, because this repo ships no git hooks, but a scaffolded project with a pre-commit hook that reformats files would hit it. Blueprint documents the trap (`bp:global-claude-md.example:312`).
- **Proposed change:** chain with `&&` and say to stop and report if the commit fails.

### 11. K8: Ignore `CLAUDE.local.md`

- **Class / effort / risk:** Patch / S / none.
- **Our gap:** the memory documentation names `CLAUDE.local.md` as the personal per-project file and says to gitignore it. `.gitignore:29` ignores `.claude/settings.local.json` and explains why, but not this.

### 12. K9: Say in `CONTRIBUTING.md` that the changelog is updated

- **Class / effort / risk:** Patch / S / none.
- **Our gap:** `CONTRIBUTING.md` and the PR template mention the changelog zero times, though it is kept carefully; the contributing bar currently ends at "fill in the PR template" (`CONTRIBUTING.md:64`).
- **Blueprint:** enforces it with a fragment-file workflow and a CI job. That is dropped (see below); one sentence is the proportionate version.

### 13. K11: `init-project` scaffolds secret scanning

- **Class / effort / risk:** Minor / L / blocked on **Decision B**. It touches `init-project`, `scripts/simulate_init.sh`, `scripts/check_scaffolded_project.sh` and their tests, and a new CI job could fail a project that already holds a secret.
- **Our gap:** nothing we ship or scaffold scans for committed secrets. `SECURITY.md:20` covers Dependabot only; the deny list (`.claude/README.md:117`) stops Claude reading secret files, not committing them; `.gitignore:2` stops some being added.
- **Blueprint:** extends the default rules of a scanner, keeps a documented allowlist where each entry names the finding it exists for and is path-scoped so a real secret elsewhere in the file is still caught, and runs it both at commit time and as the CI gate (`bp:.gitleaks.toml:14`, `:17`, `:25`; `bp:.gitlab-ci.yml:640`).
- **Where it belongs:** not in our own CI (nothing here to scan) but in what `init-project` generates, since it already writes the project's CI (`.github/workflows/skills-ci.yml:8`).

### 14. K12 (optional): a `.gitattributes`

- **Class / effort / risk:** Patch / S / none. No recorded incident: all 57 tracked files are LF today. Included only because the cost is about zero and a CRLF checkout of bash scripts fails invisibly on Windows.
- **Proposed change:** `* text=auto` and `*.sh text eol=lf` (`bp:.gitattributes:16`). Do not copy its `merge=union` on lockfiles, which can write a structurally invalid file.

## Decisions needed from the maintainer

These are outward-facing or involve terms I could not verify, so they are not mine to make.

- **Decision A, tags.** Create tags and releases for `v1.0.0` through `v2.1.0`, or keep the project untagged and point the changelog links somewhere that exists. K7's data fix depends on this.
- **Decision B, secret-scanning mechanism.** The scanner's own binary, the vendor's GitHub action (its terms for organisation-owned repositories were not checked), or GitHub's built-in secret scanning and push protection, which is a repository setting that needs no files. K11 depends on this.

## Suggested follow-on missions

Each is its own piece of work with its own plan. All would ride the pending release.

1. **Docs and config truth:** K1, K3, K8, K9, K10, K12.
2. **Wiring and registration checks:** K2a, K2b, K6.
3. **Gate and test-writing rules:** K5, K13.
4. **`/adr`:** K4.
5. **Release state:** K7, plus Decision A.
6. **Secret scanning:** K11, plus Decision B.

## Deferred

| ID | What | Revisit when |
|---|---|---|
| D1 | Pin-aware doctor / dev-tool check (ruff and pytest versions vs requirements-dev.txt pins, shellcheck present). Real mismatch seen this session (ruff 0.15.20 vs 0.16.8 pin) but no PR recorded as red because of it, and blueprint's doctor only prints versions, so this would be new work. Revisit if one goes red. | a pull request goes red because of a local tool-version mismatch |
| D2 | completeness-check: an independent fresh-agent review before push. Method is generic but wired to GitLab issues; CONTRIBUTING.md:7 says no issue is required, the harness already has a code-review skill, and no recorded miss shows the need. | reviews keep missing the same class of defect, or an issue-driven workflow is adopted |
| D3 | Local pre-push git hook running the check list. K2b and K3 give the same assurance in CI without a per-clone install; a hook only protects a clone after setup has linked it in. | K2b and K3 still let a locally green change fail in CI |
| D4 | Migrate commands/ to skills/ with disable-model-invocation. Docs say commands keep working, so nothing forces it; it would be a Major change for every downstream project with no demonstrated benefit. K1 fixes the wrong text without it. | a feature needs skills-only frontmatter, or `commands/` is deprecated |
| D5 | A 'what you can delete' guide, with a way for sync to remember a declined file. Real design gap: sync has no decline mechanism (only LOCAL_ONLY) and a removed template file would be re-offered. No incident yet, and the guide is useless until that is solved. | sync gains a way to remember a declined file |

## Dropped

Each failed one of: out of scope for a stack-agnostic template (`CONTRIBUTING.md:85`), bound to GitLab or an issue workflow we do not use, not worth its cost here, or already covered.

| ID | What | Why |
|---|---|---|
| X1 | Changelog fragments (changelog.d/, assembler, changelog-check job) | One recorded CHANGELOG conflict in 13 merges of a solo repo; the assembler needed its own silent-corruption fix; every clone would inherit 300+ lines of machinery. K9 is the proportionate version. |
| X2 | Fast-paths-by-change-class gate table | Pays off only with many review gates; our template has one fixed check list. Revisit if we add gates. |
| X3 | Follow-up-naming CI check and the Requirements / Gates ledger in PR descriptions | Anchored to GitLab issues and MR descriptions with no issue policy here, and the gate ledger only means something with many gates. |
| X4 | Blueprint's declarations file and 600-line load-bearing gate | Built for dozens of call sites; we have about one, and K2a derives it from a naming rule instead. The idea is kept, the mechanism is not. |
| X5 | SIGPIPE static scanner | Our 6 head -n1 sites all read tiny bounded input, so there is no exposure to guard. |
| X6 | Subagent fan-out ceiling | None of our commands or skills spawn subagents, so the rule has no subject. |
| X7 | Hard deny on force-push and merge commands | Our ask rules are deliberate (a deny sends someone editing settings mid-incident) and we do not assume a forge CLI. |
| X8 | kaizen-declined.json ledger | Our deterministic checks already suppress with inline markers and no snapshot shows a judgment audit re-raising a declined item. |
| X9 | Blueprint's three Claude hooks (post-edit-checks, pre-tool-safety, on-stop) | Hardcode models.py/views.py/.tsx; the first two write to a channel Claude never reads so they do nothing as written; the third is an unwired example. |
| X10 | The web-app review agents (architect, UX, accessibility, RBAC, perf, schema, OWASP, threat-model) and agents overlapping dependency/docs | Web-application subject matter, which CONTRIBUTING.md:85 puts out of scope; the rest duplicate our dependabot and docs-updater skills. |
| X11 | GitLab/milestone-bound skills (kickoff, mr, fix-mr, mass-merge, batch, dotplanning, import-spec, tracker-hygiene, ci-debug, kaizen, incident-postmortem, release) | Bound to glab, MRs and milestones; kickoff duplicates init-project. The generic core of release became K7. |
| X12 | Web-product skills (voc, voc-audit, sunset-check, import-design) | Persona panels and UI design, not stack-agnostic template content. |
| X13 | review and memory-audit skills | review duplicates the harness code-review skill; memory-audit sweeps one person's ~/.claude store, which skills/README.md:9 rules out. |
| X14 | Makefile facade, git hooks, setup-hooks.sh | Session Config plus the SessionStart warning already do the job without requiring make; hooks need a per-clone install. |
| X15 | Stack- and app-bound files: .env.example, nightly load-test budget, Helm/compose/migration/serializer/websocket/complexity/OSV scripts | Hardcoded stack or application content; the budget file ships an empty config with nothing to measure. |
| X16 | Forge-bound scripts: issue collision, MR follow-ups, release-pipeline, tag-only jobs, artifact assertions, stale references, wt | Need the GitLab API or an issue workflow we do not have. |
| X17 | Issue and MR templates, Renovate, per-stack ci/ includes, docs site, docs/releases | GitLab quick-action syntax and Renovate versus our GitHub setup; our PR template is richer; init-project already generates the per-stack CI. |
| X18 | global-claude-md.example | Personal user-level instructions by the docs' own definition; 542 lines against a 200-line target and largely restating the project file. |
| X19 | merge=union on lockfiles | Union merge can write a structurally invalid file, and blueprint itself says it hides defects on the merged tree. |
| X20 | Shipping .example rule stubs for backend/frontend/tests | Stack-bound content; the mechanism worth keeping is K5's path-scoped rule. |
| X21 | customize.sh and the docs-link gate | check_scaffolded_project.sh, init-project and check_inherited_docs.sh already do both jobs. |

## How far to trust blueprint

Three of its statements about itself or about Claude Code are contradicted by the evidence, so its self-reported figures (13,000 pipeline runs, "16 of 20 merged MRs had gaps", token-cost numbers) should be treated as unverified:

- **Counts.** Its project description says 14 agents and 13 commands; its tree has 17 agent files and 20 skills, and its own `bp:CLAUDE.md:648-667` lists 20 skills.
- **A "one-line import".** `bp:CLAUDE.md:299` calls `ci/CLAUDE.md` a one-line `@` import of `scripts/CLAUDE.md`; the file is 240 lines, most of it Helm-specific.
- **The `paths:` loader.** `bp:CLAUDE.md:285` says Claude Code has none; the current memory documentation says it does (see K5).

Its root `CLAUDE.md` is 775 lines against the documentation's target of under 200, and two of its three Claude hooks write to a stream Claude does not read (K6).

## Method and limits

- **Read in full or in part:** blueprint's `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CHANGELOG.md` and `LICENSE`; all 17 agents and 20 skills by frontmatter, and about ten of them in depth; its `.claude/settings.json` and four hooks; its `Makefile`, git hooks, `.gitleaks.toml`, `load-bearing.declarations`, `.gitattributes`, `doctor.sh`, the head of its changelog assembler and version gate, and `docs/adr/README.md`; its CI job list and templates.
- **Classified from a header comment only:** about 30 of its 40 scripts (12,040 lines in all).
- **Not read:** its per-stack CI includes (`ci/python.yml` and the rest), its documentation website, and `docs/releases/`.
- **Counts of forge and stack markers** per agent and skill were a crude heuristic. They undercount subject-matter binding (its UX agents score zero and are plainly web-UI work).
- **Claude Code behaviour** (hook output streams, skills, rules, memory) comes from the official documentation fetched through a summarising tool on 2026-10-03, and was cross-checked against the saved page text and this session's own behaviour. Re-read the page before changing anything on its strength.
- **Measured here, not argued:** the hook-wiring experiment (K2a), the list of tags and releases (K7), the absence of secret scanning (K11), the CRLF check (K12), and the test-script parity (K2b) were each run against this repo.
- **Method:** each finding was tested against four questions (in scope, GitLab-only, downstream cost, already covered) plus a tie-break: no evidence of harm means defer or drop, unless the cost is about zero. All note citations were checked mechanically against the pinned blueprint commit and this repo.
- **Licence:** blueprint is Apache-2.0 (`bp:LICENSE:2`) and this repo is MIT. Copying files or text would bring Apache's redistribution terms (give recipients the licence, mark changed files, retain notices). Re-implement; do not paste. This is not legal advice.
