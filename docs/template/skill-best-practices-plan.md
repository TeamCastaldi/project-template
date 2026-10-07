# Plan: adopting the skill best-practices review

Status: **Phase 0 complete (both decisions recorded); Phase 1 not started.** Written 2026-10-07 from [`skill-best-practices-review.md`](skill-best-practices-review.md) ("the review"). Item IDs (S1–S8, N1–N7, Decisions A and B) are the review's. Blueprint review items are prefixed `K` and its decisions are named in full, because both reviews have a "Decision A".

Each phase is one branch and one pull request, named by `CONTRIBUTING.md`'s convention. The phases are ordered by dependency: an earlier phase never waits on a later one. Line numbers cited in the review will drift as phases land, so every phase starts by re-reading the files it changes rather than trusting a citation.

## Concern tracker

Every concern the review raised, and where it is closed. Tick a row when its phase merges.

| Concern | Review ID | Phase | Done |
|---|---|---|---|
| Where evaluations live | Decision B | 0 | [x] |
| Whether commands block model invocation | Decision A | 0 (decide), 8 (apply) | [ ] |
| Script paths fail from the repo root | S2 | 1 | [ ] |
| `sync-from-template` tells Claude to read its script before running it | S2 | 1 | [ ] |
| No evaluations; untested on Haiku, Sonnet and Opus | S6 | 2 | [ ] |
| Two descriptions over 1,024 characters | S1 | 3 | [ ] |
| "Nathan" vs "the user" across skills | S4 (terminology) | 3 | [ ] |
| Validator checks presence only, and has no test | S5 | 4 | [ ] |
| `init-project` too long to survive compaction | S3 | 5 | [ ] |
| Stale wording in `init-project` | S3 | 5 | [ ] |
| Maintainer rationale inside `init-project` | S3 | 5 | [ ] |
| Body text that only matters before a skill triggers, or only to maintainers | S4 | 6 | [ ] |
| No progress checklist in `dependabot` | S8 | 6 | [ ] |
| No authoring rules for new skills | S7 | 7 | [ ] |
| Stale "skills cannot be invoked by name" text | K1 (blueprint) | 8 | [ ] |
| Review status, changelog, version and downstream check | — | 9 | [ ] |
| Gerund renames, third-person rewrites, portable frontmatter, tables of contents, MCP names, wholesale prose cuts, splitting `dependabot` | N1–N7 | No action | — |

N1–N7 are closed by not doing them. The review gives a reason for each. If a later phase makes one apply (N4 becomes a rule once Phase 5 creates reference files), that phase says so.

## Standard gate

Every phase passes this before its pull request is opened. It is `CONTRIBUTING.md`'s local check list, plus the two checks it currently omits:

1. The full list under `CONTRIBUTING.md` → "Open a PR", run as written.
2. `shellcheck` over every `.sh` file. CI runs it; the local list does not yet (blueprint K3).
3. The scaffold smoke test, because every phase touches files a scaffolded project inherits:

   ```bash
   bash scripts/simulate_init.sh python-cli /tmp/scaffold-check
   bash scripts/check_scaffolded_project.sh /tmp/scaffold-check
   ```

4. A `CHANGELOG.md` line under `## [Unreleased]`, in the section the phase names.

## Phase 0: Decisions

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| Decisions A and B | none | S | — | none (edit this file) |

No code. Two answers, recorded in the decision log at the bottom of this file.

1. **Decision B: where evaluations live.** This blocks Phase 2. The review recommends inside each skill folder, at `evals/evals.json`, which is where skill-creator expects them. They cost no context unless read, and `sync-from-template` delivers them downstream.
2. **Decision A: whether commands set `disable-model-invocation: true`.** This only blocks Phase 8, so it can wait until then. If the answer is yes, it also decides what happens to `/commit-msg`: `/session-end` Step 3 has Claude run it. This plan recommends leaving `/commit-msg` model-invocable: it is read-only and never commits.

**Done when:** both decisions are in the decision log, or Decision A is explicitly deferred to Phase 8.

## Phase 1: Fix the bundled-script paths

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S2 | Patch | S | — | `fix/skill_script_paths` |

1. `dependabot/SKILL.md`: in Phase 2's pipeline, change `python3 scripts/categorize_prs.py` to `python3 .claude/skills/dependabot/scripts/categorize_prs.py`. Use the same full path in the "Bundled script" note.
2. `sync-from-template/SKILL.md`, step 1: change the command to `bash .claude/skills/sync-from-template/scripts/compare_template.sh …`. The markdown link targets can stay relative, because links resolve from the file; only the command runs from the shell's working directory.
3. Same file: replace "worth reading rather than trusting blindly" with an instruction to read the script only if its output is not what the step describes.
4. Do not switch to `${CLAUDE_SKILL_DIR}`. It expands to an absolute path that the repo-relative allow rules in `.claude/settings.json` would not match.

**Verify** (from the repo root, after committing):

```bash
echo '[]' | python3 .claude/skills/dependabot/scripts/categorize_prs.py   # prints [] and exits 0
bash .claude/skills/sync-from-template/scripts/compare_template.sh \
  "$PWD" "$(git branch --show-current)" "$PWD" .claude                     # every row SAME
grep -n 'scripts/categorize_prs.py\|scripts/compare_template.sh' .claude/skills/*/SKILL.md
```

The comparison clones the local repo, which is why it runs after committing. Git warns that `--depth` and `--filter` are ignored for a local clone; that is harmless. Remove the `TEMP_CLONE` it prints afterwards. Dry-run on 2026-10-07 against the unchanged scripts, with the paths already written in full: `[]` with exit 0, and 33 `SAME` rows.

**Done when:** both commands succeed, and every `grep` hit is a full `.claude/skills/…` path or a markdown link target.

**Changelog:** `### Fixed`. `dependabot` and `sync-from-template` now name their scripts by repo-relative path; the bare `scripts/…` form resolved to the root `scripts/` folder and failed.

## Phase 2: Evaluation baseline

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S6 | Minor | M to L | Phase 0 (Decision B) | `test/skill_evals` |

The evaluations come before any text changes, so Phases 3, 5 and 6 can be measured against a baseline. If this phase slips, those phases may land with a manual check in a fresh session for each changed skill, and the evaluations are run against them retroactively.

1. Install the skill-creator plugin in a local Claude Code session. The Claude Code skills page gives the command: `/plugin install skill-creator@claude-plugins-official`.
2. Write `.claude/skills/<name>/evals/evals.json` for each skill (Decision B), with these three cases. Each case needs a fixture, kept beside it in `evals/`. CI runs `pytest` and `ruff` over all of `.claude/skills`, so give code fixtures a non-`.py` extension, such as `stub_only_assertion.py.txt`. Then neither tool collects or lints a deliberately bad example. The behaviour cases are chosen so that none needs a live pull-request queue.

   | Skill | Should trigger | Should not trigger (near-miss) | Behaviour |
   |---|---|---|---|
   | `dependabot` | "There are nine open Dependabot PRs here, clean them up" | "Bump requests to 2.32 in the manifest" (a manual edit) | With `gh` unauthenticated or a dirty working tree, it stops at Phase 0 and never runs `gh pr list` |
   | `docs-updater` | "I just added the export command, update the README to match" | "Write the session snapshot and wrap up" (`/session-end`) | An architecture change produces an ADR file, an Index row and a one-line Decision log link, with no reasoning pasted into `CLAUDE.md` |
   | `init-project` | "I just cloned this template, help me set it up" | "Start a coding session" (`/session-start`) | The first reply asks exactly one question and previews none of the others |
   | `sync-from-template` | "Is this repo behind project-template? Pull any newer skills" | "Check this repo's READMEs against its folders" (`/sync-template`) | A `LOCAL_ONLY` file is reported and left untouched, even after `SYNC: PULL ALL` |
   | `testing-standards` | "Write a test for the date-parser bug I just fixed" | "Set up pytest in this project" (runner config, not a test) | Reviewing a test whose only assertion is `assert_called_once()` on an incoming stub flags it as M2 |

3. Run every case with the skill and without it, each in a fresh session. Do this for each model family the template is meant to support (the guide names Haiku, Sonnet and Opus), and note which families were not available.
4. Record pass rates per skill and per model in a new `docs/template/skill-eval-baseline.md`. It lives in `docs/template/` because it is about the template and must not travel downstream.

**Verify:**

```bash
find .claude/skills -path '*/evals/evals.json' | wc -l   # 5
find .claude/skills -path '*/evals/*' -name '*.py'        # nothing
python3 -m pytest .claude/skills -q --collect-only | tail -1   # same count as before this phase
```

Also check that each file parses as JSON with at least three cases, and run the standard gate. `ruff` and `validate_skills.sh` must stay clean with the new files present.

**Done when:** 15 cases exist, each with its fixture, and a baseline is recorded for at least one model family. Families not run are listed as gaps.

**Changelog:** `### Added`. Three evaluations per skill, in skill-creator's format, in each skill's `evals/` folder, and how to run them. Note that synced projects receive them, cost no context unless run, and are re-offered them if deleted.

**Coordination:** blueprint K13 adds two smells to `testing-standards`. If K13 lands after this phase, re-run that skill's baseline before using it to judge Phase 6.

## Phase 3: Descriptions and terminology

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S1; S4 (terminology) | Patch | S | Phase 2 (baseline) | `docs/skill_descriptions` |

1. Replace the `description` of `init-project` and of `sync-from-template` with the review's proposed folded text (796 and 687 characters).
2. In `sync-from-template` (body and config comments) and `docs-updater` (description and body), change "Nathan" to "the user". Keep the `TeamCastaldi/project-template` URL; that is a fact, not a name for the reader.

**Verify:**

```bash
python3 -m pip install pyyaml   # one-off, local only; Phase 4 makes the validator do this
python3 - <<'EOF'
import glob, re, yaml
for f in sorted(glob.glob('.claude/skills/*/SKILL.md')):
    fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---', open(f).read(), re.S).group(1))
    print(len(fm['description']), f)
EOF
grep -c Nathan .claude/skills/*/SKILL.md     # all 0
```

Then re-run the trigger and near-miss cases for both changed skills.

**Done when:** every description is ≤ 1,024 characters, and trigger results equal or beat the Phase 2 baseline.

**Changelog:** `### Changed`. Shorter `init-project` and `sync-from-template` descriptions, within the 1,024-character limit for uploads and the Skills API, with the same trigger phrases.

## Phase 4: The validator enforces the guide's limits

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S5 | Minor | M | Phase 3 merged | `feature/validate_skill_limits` |

Minor because `validate_skills.sh` is in `tooling_paths.txt` and ships downstream: a project that has added a non-conforming skill will newly fail. That is the purpose. Say so in the changelog entry.

1. Make the frontmatter reader return a whole value: join the lines of a folded or literal block, and strip the quotes from a quoted one. Today it returns only the first line, by design.
2. Add the checks, each as a `PROBLEMS` row in the existing tab-separated format:
   - `NAME_FORMAT`: the name is not `^[a-z0-9-]{1,64}$`
   - `NAME_RESERVED`: the name contains `anthropic` or `claude`
   - `DESC_TOO_LONG`: the description is over 1,024 characters
   - `XML_IN_FRONTMATTER`: the name or description contains an XML-like tag
   - `BODY_TOO_LONG`: the body after the frontmatter is over 500 lines
3. Print a `WARN` row, not counted in `PROBLEMS`, for a body over 20,000 characters. That is roughly where compaction cuts a skill (S3). `init-project` triggers it until Phase 5.
4. Update the script's header block to list the new checks.
5. Write `scripts/test_validate_skills.sh` with one fixture per check, plus a passing fixture with a folded description. Show that the new cases fail against the unchanged script before the fix lands.
6. Register the test in every place a test script is registered today:
   - `.github/workflows/skills-ci.yml`
   - `CONTRIBUTING.md`'s check list
   - an allow rule in `.claude/settings.json`
   - `scripts/README.md`
   - `.claude/skills/sync-from-template/tooling_paths.txt`, beside `validate_skills.sh`

   Five places by hand is the drift blueprint K2b describes. If K2b's derivation check lands first, it does this registration for you.

**Verify:**

```bash
bash scripts/test_validate_skills.sh
bash scripts/validate_skills.sh          # PROBLEMS=0; one WARN for init-project until Phase 5
bash scripts/check_doc_claims.sh         # the new allow rule names a script that exists
```

**Done when:** all of the above pass. As a side effect, `scripts/README.md`'s claim that every check script "has a `test_*.sh` beside it" becomes true for `validate_skills.sh`.

**Changelog:** `### Added`, for the new checks and their test. Note that downstream projects may newly fail, and name the fix: shorten the description, or split the body.

## Phase 5: Restructure `init-project`

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S3 (all parts) | Patch | M | Phase 2 (baseline); Phase 4 helps | `refactor/init_project_disclosure` |

Content moves verbatim. Only the pointers and the stale phrases are new text.

1. Directly under the title, add a progress checklist for Claude to copy into its reply. It names Phases 0–7 and ends with the gate: `bash scripts/check_scaffolded_project.sh` exits 0.
2. Move three sections into `references/`, each replaced by a one-line pointer that says when to read the file:
   - **`references/inherited-docs.md`:** Phase 4 in full, including "Verify before moving on". Phase 0's retrofit branch points here too.
   - **`references/cloud-environment.md`:** "Recommend the cloud environment settings". Phase 3's last step and Phase 7's restatement both point here.
   - **`references/foundation-template.md`:** Phase 6's markdown template. Phase 6's instructions about honesty and the Status line stay in `SKILL.md`.
3. Move "Why this skill owns the docs pass" into `.claude/README.md`, as a short subsection beside the other design notes.
4. Fix the stale wording:
   - "workflow prompts" in the Role section becomes "commands and skills"
   - "template-sync workflow" becomes `/sync-template`
   - "session-start workflow … once those exist" becomes `/session-start`, with "once those exist" dropped
5. Keep every reference one level deep. No file in `references/` links to another one. Phase 4's content is under 100 lines, so N4 (tables of contents) does not apply yet.
6. Check what cites the phases: `simulate_init.sh` and `check_scaffolded_project.sh` mention phases by number in comments. The numbers do not change, so expect no edits, but confirm.

**Verify:**

```bash
wc -c .claude/skills/init-project/SKILL.md          # about 18,500 or less
head -40 .claude/skills/init-project/SKILL.md       # the checklist and its final gate are visible
d=.claude/skills/init-project
for f in $(grep -o 'references/[a-z-]*\.md' $d/SKILL.md | sort -u); do [ -f "$d/$f" ] || echo "MISSING $f"; done
bash scripts/validate_skills.sh                     # no WARN for init-project
```

`check_inherited_docs.sh` does not sweep `.claude/skills/`, so the link loop above is the only link check here. Then run the standard gate's scaffold smoke test and all three `init-project` evaluations, compared against the baseline.

**Done when:** the checklist with the gate sits in the first 40 lines, the size warning is gone, no link is missing, and the evaluations hold the baseline.

**Changelog:** `### Changed`. `init-project` keeps its closing gate within the part Claude Code keeps after compaction, and loads Phase 4, the cloud settings and the brief template only when it reaches them.

## Phase 6: Body trims and the `dependabot` checklist

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S4 (rest); S8 | Patch | S | Phase 2 (baseline) | `refactor/skill_body_trims` |

1. **`sync-from-template`:**
   - Cut "When to use this" down to the one sentence that separates it from `/sync-template`.
   - Delete the note about `init-project` maybe recording the template origin "later". If that ever happens, the same change updates this skill.
   - Move the ephemeral-clone rationale into `compare_template.sh`'s header comment. This is a comment-only change to the script.
2. **`dependabot`:**
   - Before deleting "Edge cases", map each of its bullets to the phase that already states the rule, as a table in the pull request description. A bullet with no home gets moved into its phase, not dropped.
   - Fold "Bundled script" into Phase 2 as a two-line statement of the script's input and output.
   - Add a copyable progress checklist under the title: Phases 0–7, with the Phase 5 confirmation gate marked.

**Verify:**

```bash
wc -c .claude/skills/sync-from-template/SKILL.md .claude/skills/dependabot/SKILL.md   # about 3,400 fewer combined
grep -c 'No open Dependabot PRs found. Exiting.' .claude/skills/dependabot/SKILL.md       # still ≥ 1
grep -n 'gh auth login\|cherry-pick --abort\|Do not close any original PR' .claude/skills/dependabot/SKILL.md
shellcheck .claude/skills/sync-from-template/scripts/compare_template.sh
```

Then run the evaluations for both skills, compared against the baseline.

**Done when:** every edge-case rule can still be found in its phase, the evaluations hold the baseline, and the character reduction is in the expected range.

**Changelog:** `### Changed`. A leaner `sync-from-template` and `dependabot`, and a progress checklist for `dependabot`.

## Phase 7: Authoring rules for new skills

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| S7 | Patch | S | Phases 1–6 | `docs/skill_authoring_guide` |

This comes last among the content phases, so it describes what the repo now does rather than what it intends to do.

1. Add a "Writing a skill" section of about ten lines to `.claude/skills/README.md`:
   - a link to the guide
   - the limits Phase 4 enforces
   - descriptions say what and when, with trigger phrases first
   - the body holds only what Claude needs to act; maintainer rationale goes in a README
   - must-not-lose instructions, and a progress checklist for long workflows, go near the top
   - reference files sit one level deep, with a table of contents once they pass 100 lines (N4 becomes a rule here)
   - scripts are named by repo-relative path
   - three evaluations in the skill's `evals/` folder, run in a fresh session before merge, with code fixtures named so `pytest` and `ruff` skip them
2. Say that evaluations are not run in CI, because they need a model, and point to Phase 2's how-to.

**Verify:** each rule matches something enforced or practised: a validator check, an existing skill, or the evaluation files. Run `/sync-template`; it should report no drift.

**Done when:** every rule in the section points at a real check or example in the repo.

**Changelog:** `### Added`. Authoring rules for skills in `.claude/skills/README.md`.

## Phase 8: Command invocation

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| K1; Decision A | 8a Patch; 8b Major | S | Phase 0 (Decision A) | `docs/command_invocation` |

**8a, always:** fix the stale premise (blueprint K1).

1. `.claude/README.md`'s "signs you chose wrong" bullet says the dispatcher exists "only because skills cannot be invoked by name". Correct it: any skill can be invoked by `/name`.
2. Describe the real axis, who may start it, in the mechanism tables. Name the two frontmatter fields: `disable-model-invocation: true` (only the user) and `user-invocable: false` (only Claude).
3. Re-read the other passages K1 names (`.claude/README.md`'s tree, `.claude/skills/README.md`'s opening, root `README.md` step 2). Change only what is still false.

**8b, applies: Decision A was yes (2026-10-07):**

4. Add `disable-model-invocation: true` to `/audit-tests`, `/branch-workflow`, `/roadmap`, `/session-end`, `/session-start` and `/sync-template`. Leave `/commit-msg` as Decision A recorded.
5. In `session-start.md`'s Close section, change "offer to run `/session-end`" to telling the user to type `/session-end`.
6. In `.claude/README.md`'s "Which of the three" table, the Command column now matches the field: a command is decided by the user, and enforced.

**Verify** in a fresh session:

- "Wrap up the session" gets a suggestion to type `/session-end`, not a run of it.
- Typing `/session-end` still works, and its Step 3 still drafts the message through `/commit-msg`.
- The Skills row in `/context` shrinks by about the size of the six descriptions.

**Done when:** 8a and 8b are merged, with the checks above passing.

**Changelog:**

- 8a: `### Fixed`. The docs no longer say skills cannot be invoked by name.
- 8b: a Major entry. Six commands no longer start on their own, and their descriptions leave the skill listing. All files are under `.claude/`, so no `### Migration steps` list is needed; the entry's prose is shown to whoever syncs.

## Phase 9: Close-out

| Addresses | Class | Effort | Depends on | Branch |
|---|---|---|---|---|
| Release and records | — | S | Phases 1–8 | `docs/skill_review_closeout` |

1. Re-run all 15 evaluations on every model family available, and add the final numbers beside the baseline in `skill-eval-baseline.md`.
2. Change the review's status line from "proposal only" to "adopted", with links to this plan and the merged pull requests.
3. The pending release is Major (3.0.0), because Decision A was yes and 8b changes who may start a command. Update `.template-version` when the release is cut, not before.
4. Check the downstream path. Run `compare_template.sh` from a scaffold built by `simulate_init.sh` against this repo's merged branch, and confirm every change arrives as `NEW` or `CHANGED`, with nothing needing a migration step.
5. Tick every row of the concern tracker, and set this plan's status to "complete".
6. Write the session snapshot to `docs/template/`.

**Done when:** every tracker row is ticked, or says "No action", and the downstream comparison shows no surprises.

## Decision log

| Decision | Answer | Date | Notes |
|---|---|---|---|
| B: where evaluations live | **In each skill folder** (`.claude/skills/<name>/evals/`) | 2026-10-07 | skill-creator's default, and they change in the same PR as the skill. They reach every project at clone and on sync. A project that deletes them is re-offered them on each sync (blueprint D5). Sample files must not be collected by `pytest` or linted by `ruff` (Phase 2). |
| A: commands set `disable-model-invocation: true` | **Yes** | 2026-10-07 | `/commit-msg` stays model-invocable, as recommended, so `/session-end` Step 3 keeps working. Confirm or overturn that before Phase 8. |
