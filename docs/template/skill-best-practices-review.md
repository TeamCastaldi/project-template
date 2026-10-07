# Skill authoring best practices review: what Anthropic's guide means for this template

Status: **adopted, pending merge.** Every change below is implemented in the stacked pull requests #29 to #37 and the close-out that follows them, tracked in [`skill-best-practices-plan.md`](skill-best-practices-plan.md). S6's evaluations are written but not yet run. Written 2026-10-07 against this repo at `main` (46137e4) and Anthropic's [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (called "the guide" below), fetched the same day as raw markdown.

Citations: our files as `path:line`. Line numbers will drift as files change. Claude Code–specific behaviour is cited from the [Claude Code skills page](https://code.claude.com/docs/en/skills), fetched the same day, and labelled as such wherever it differs from the guide.

## Summary

The guide covers how to write a `SKILL.md` that Claude finds and follows. In short: keep it concise, because context is shared; write a description that says what the skill does and when to use it; disclose detail progressively through files one level deep; bundle scripts that solve problems instead of passing them back to Claude; and prove the skill works with evaluations, not opinion. It also sets hard frontmatter limits.

This repo already does most of what the guide asks of the **machinery around** a skill. Its bundled scripts are stdlib-only, document their own constants, and handle their own errors. Validator feedback loops (`validate_test_audit.py`, `check_scaffolded_project.sh`, `check_roadmap.sh`) match the guide's "run validator, fix, repeat" pattern. Exact gate phrases match its "low freedom" advice for fragile steps. The gaps are in the **skill files themselves**:

1. **Two descriptions break the guide's 1,024-character limit.** `init-project` is 1,307 characters and `sync-from-template` is 1,302. Claude Code's listing allows 1,536, so nothing breaks here today. The guide's limit applies anywhere else these skills might be uploaded or packaged, and `validate_skills.sh` can't see the overrun (S1, S5).
2. **`init-project` is too long to survive context compaction intact.** It is about 7,400 tokens. After compaction, Claude Code keeps only the first 5,000 tokens of an invoked skill, and that cut falls mid-Phase 4. The part that would be lost includes the closing `check_scaffolded_project.sh` gate, in the skill most likely to run long enough to compact (S3).
3. **`dependabot`'s script command fails as written.** Running it from the repo root reproduces `can't open file '.../scripts/categorize_prs.py'`. `sync-from-template` uses the same path shape (S2).
4. **No skill has an evaluation.** Every item in the guide's Testing checklist is unchecked. Tooling for this now exists, which the guide doesn't yet mention (S6).
5. **`validate_skills.sh` only checks that fields exist.** None of the guide's limits are enforced, so the first finding passes CI (S5).

Of the guide's checklist, **8 changes are worth doing** (7 firmly, 1 optional), **2 decisions** need the maintainer, and **7 items are deliberately not recommended**, with a reason for each.

## How the guide maps onto this repo

| Guide says | Here | Evidence |
|---|---|---|
| `name` ≤ 64 chars, lowercase/digits/hyphens, no "anthropic" or "claude" | ✅ All five pass | Not enforced by `validate_skills.sh` (S5) |
| `description` ≤ 1,024 chars, no XML tags | ❌ 2 of 5 over | `init-project/SKILL.md:3` (1,307), `sync-from-template/SKILL.md:3` (1,302) |
| Description says what **and** when, third person, key terms | ✅ All five | The two long ones also carry implementation detail that belongs in the body |
| `SKILL.md` body under 500 lines | ✅ Largest is 389 (`dependabot`) | But see compaction (S3) |
| Progressive disclosure, references one level deep | ⚠️ Layout sanctioned, never used | `.claude/skills/README.md:28` shows `references/`; no skill has one |
| Table of contents in reference files over 100 lines | n/a | No reference files yet |
| No time-sensitive information | ⚠️ A few stale phrases | `init-project/SKILL.md:12`, `:267` (S3) |
| Consistent terminology | ⚠️ "the user" vs "Nathan" | `sync-from-template` says "Nathan" 10 times; `dependabot` and `init-project` say "the user" |
| Clear workflow steps, copyable checklists | ✅ Phases and gates; ⚠️ no progress checklist in the two longest | S8 |
| Feedback loops for quality-critical work | ✅ | `audit-tests.md:89-97`, `init-project/SKILL.md:257-263` |
| Scripts solve, don't defer; no "voodoo constants" | ✅ | e.g. `compare_template.sh:52` explains `--depth 1 --filter=blob:none` |
| File paths resolve; execution intent is clear | ❌ One broken, one ambiguous | `dependabot/SKILL.md:101`, `sync-from-template/SKILL.md:79`, `:86-88` (S2) |
| Required packages listed | ✅ | `dependabot` `compatibility:`; scripts are stdlib-only |
| Fully qualified MCP tool names | n/a | No skill names an MCP tool |
| Forward slashes only | ✅ | No backslash paths found |
| At least three evaluations; tested on Haiku, Sonnet and Opus | ❌ None | S6 |

## Findings worth doing, in suggested order

Effort is a rough guide (S under an hour, M a few hours, L a day or more). The SemVer class follows `CHANGELOG.md`'s definitions as they apply to a downstream project. Every change below lives under `.claude/` or in `tooling_paths.txt`, so `sync-from-template` delivers it downstream without a Migration steps entry.

### 1. S1: Bring the two long descriptions under 1,024 characters

- **Class / effort / risk:** Patch / S / low. Every trigger phrase is kept; re-check triggering in a fresh session.
- **Guide:** `description` "Maximum 1,024 characters". The description decides *when*, "while the rest of SKILL.md provides the implementation details."
- **Our gap:** both descriptions spend characters on *how*. `init-project` explains Phase 4's retrofit history. `sync-from-template` explains its migration batching, and lists `/sync-from-template` as a trigger phrase, though typing that already invokes the skill directly. Both are also among the longest entries in every session's skill listing, here and in every project scaffolded from this template.
- **Proposed text** (796 and 687 characters):

  ```yaml
  # init-project
  description: >-
    Runs the one-time setup for a project freshly cloned from this stack-agnostic template:
    interviews the user one question at a time on identity, shape, stack and constraints,
    proposes a scaffolding plan for approval, then creates folders and root tooling, re-points
    the inherited docs (CONTRIBUTING.md, SECURITY.md and the rest) at the real project, and
    fills in CLAUDE.md and docs/foundation.md. Use when the user has just cloned the template
    and wants to get started, even if they only say "help me set this up"; when CLAUDE.md's
    Project identity is still a placeholder or docs/foundation.md is missing; or when an
    already-initialized project's CONTRIBUTING.md, SECURITY.md or folder READMEs still
    describe "this template". Not for everyday session startup or for pulling later template
    updates.

  # sync-from-template
  description: >-
    Pulls newer commands, skills and the scripts they run from the upstream project-template
    repo into a project scaffolded from it, showing a diff per file and waiting for
    confirmation before overwriting anything. Also turns the Migration steps of any Major
    changelog entry in the version gap into proposed deletions and edits. Use when the user
    asks to sync, pull or update tooling, commands or skills from the template, says the
    template has newer tooling, asks to catch up on or migrate to a newer template version, or
    asks whether this repo is behind project-template. Not for auditing a repo's own
    consistency between folders, READMEs and CLAUDE.md; that is the /sync-template command.
  ```

  Both parse as YAML; the counts are of the parsed values.
- **Advantage:** the skills become uploadable to claude.ai and usable through the Skills API without editing, and about 1,100 characters leave the skill listing in every session.

### 2. S2: Fix the bundled-script paths in `dependabot` and `sync-from-template`

- **Class / effort / risk:** Patch / S / none.
- **Guide:** "File paths matter". Scripts should "solve, don't defer". "Make execution intent clear": run a script, or read it, not both.
- **Our gap:** `dependabot/SKILL.md:101` says `python3 scripts/categorize_prs.py`. From the repo root, that path points into the root `scripts/` folder; reproduced, it exits 2 with "No such file or directory". `sync-from-template/SKILL.md:79` has the same shape for `compare_template.sh`. Claude can recover by searching, but only after a failed call. The other skills already get this right: `init-project/SKILL.md:24` and `audit-tests.md:90` give the full repo-relative path, which is also how the allow rules in `.claude/settings.json` name scripts. Separately, `sync-from-template/SKILL.md:86-88` tells Claude to read the script before running it, "rather than trusting blindly". The guide's point about scripts is that only their output needs to cost tokens.
- **Proposed change:** use `.claude/skills/dependabot/scripts/categorize_prs.py` and `bash .claude/skills/sync-from-template/scripts/compare_template.sh`. Don't use `${CLAUDE_SKILL_DIR}`: it expands to an absolute path that the repo-relative allow rules would not match. Make the read conditional: read the script only if its output is unexpected.
- **Advantage:** both workflows succeed on the first call, without a search step.

### 3. S3: Restructure `init-project` so its closing gate survives compaction

- **Class / effort / risk:** Patch / M / low. Content moves; nothing about behaviour changes.
- **Guide:** `SKILL.md` "serves as an overview that points Claude to detailed materials as needed". Use Pattern 3 (conditional details): load a section only when the task reaches it.
- **Claude Code:** after compaction it "re-attaches the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each … put the most important instructions near the top of `SKILL.md`."
- **Our gap:** `init-project/SKILL.md` is 277 lines and 29,533 characters, about 7,400 tokens. The 5,000-token mark falls near line 168, inside Phase 4. Everything after it would be lost in a compacted session: Phase 4's verification (`:172`), Phases 5–7, and the rule that `check_scaffolded_project.sh` "must exit 0 before you call this skill done" (`:257-263`). This is the skill most likely to compact. It runs a 16-question interview one question per message, then a full scaffold.
- **Proposed change:**
  - Put a copyable progress checklist at the top that names every phase and ends with the gate itself: `check_scaffolded_project.sh` exits 0. This is the part that does the work. It puts the gate in the first few hundred tokens, whatever length the rest ends up.
  - Move three sections into files one level deep under `references/` (the layout `.claude/skills/README.md:28` already sanctions):
    - Phase 4 (`:135-193`, 7,400 characters), which the Phase 0 retrofit path also loads on its own
    - the cloud environment recommendation (`:112-133`, 2,700 characters)
    - Phase 6's `foundation.md` template (`:216-243`, 800 characters)
  - Move "Why this skill owns the docs pass" (`:269-277`) into `.claude/README.md`. It explains the design to maintainers and gives Claude nothing to do.
  - Fix stale wording on the way: "workflow prompts" (`:12`) dates from before the move to commands. "template-sync workflow" and "session-start workflow … once those exist" (`:33`, `:267`, `:274-275`) describe things that already ship in the same folder; name them `/sync-template`, `/session-start` and `docs-updater`.

  This takes about 11,700 characters out, leaving roughly 18,500 with the checklist added, or about 4,600 tokens by the same estimate. That is close to the window, which is why the checklist, not the length, is what carries the gate.
- **Advantage:** a long first-run session keeps its final gate. A retrofit run loads only Phase 4, and each run carries less context.

### 4. S4: Trim body text that only matters before a skill triggers, or only to maintainers

- **Class / effort / risk:** Patch / S / none.
- **Guide:** "Does this paragraph justify its token cost?" The description, not the body, decides when a skill is used.
- **Our gap:**
  - `sync-from-template/SKILL.md:28-41` ("When to use this") restates the description. Claude only reads the body after it has already chosen the skill. Keep the one sentence that separates it from `/sync-template`.
  - `sync-from-template/SKILL.md:130-136` (why an ephemeral clone and not a remote) and `:60-64` (what to do "if `init-project` starts doing that later") are design notes. Move them into `compare_template.sh`'s header or drop them.
  - `dependabot/SKILL.md:321-349` ("Edge cases", 1,700 characters) repeats rules each phase already states, and every bullet even cites the phase it repeats. Fold `:380-389` ("Bundled script") into Phase 2.
  - Terminology: replace "Nathan" with "the user" in `sync-from-template` and `docs-updater`, as the other three skills already do.
- **Advantage:** about 3,400 fewer characters per invocation across the two skills, with no behaviour removed.

### 5. S5: Make `validate_skills.sh` enforce the guide's hard rules

- **Class / effort / risk:** Minor / M / can newly fail a downstream project that has added a non-conforming skill, which is its purpose. `validate_skills.sh` is listed in `tooling_paths.txt`, so it ships downstream. Land S1 first, or in the same change, so CI stays green.
- **Guide:** `name` ≤ 64 characters, `[a-z0-9-]`, no XML tags, no "anthropic" or "claude". `description` non-empty, ≤ 1,024 characters, no XML tags. Body under 500 lines.
- **Our gap:** the script checks presence and the name/directory match (`scripts/validate_skills.sh:9-16`). For a folded `>` description it reads only the first line, by design (`:58-60`), so it cannot measure length. That is why S1's two overruns pass CI. Unlike the other check scripts, it has no test.
- **Proposed change:**
  - Add the checks `NAME_FORMAT`, `NAME_RESERVED`, `DESC_TOO_LONG`, `XML_IN_FRONTMATTER` and `BODY_TOO_LONG`, joining folded values so the full description can be measured.
  - Optionally print a non-failing `WARN` when a body passes about 20,000 characters (the compaction window from S3).
  - Add `scripts/test_validate_skills.sh` with one fixture per check, shown to fail against the unfixed script. Register it everywhere a test script is registered today: `skills-ci.yml`, `CONTRIBUTING.md`, `settings.json` and `scripts/README.md`. That four-place registration is the drift the blueprint review's K2b describes.
- **Advantage:** the guide's limits become a regression test, here and downstream.

### 6. S6: Give each skill three evaluations

- **Class / effort / risk:** Minor / M to L / none. Where the eval files live is Decision B.
- **Guide:** "Create evaluations BEFORE writing extensive documentation", at least three per skill. "Test with all models you plan to use" (Haiku, Sonnet and Opus). Iterate with one Claude instance authoring the skill and a fresh one testing it.
- **Our gap:** none exist. The pytest and shell suites test the scripts. Nothing tests whether a skill triggers on the right request, or whether Claude follows it once it has.
- **Newer than the guide:** the guide says there is "not currently a built-in way to run these evaluations". Claude Code's skills page now documents the `skill-creator` plugin, which provides:
  - `evals/evals.json` inside the skill directory
  - with-skill against without-skill baselines
  - description tuning from should-trigger and should-not-trigger prompts
  - blind A/B comparison of two skill versions

  It also documents `claude plugin eval`, which only applies to plugin skills.
- **Proposed change:** three cases per skill in skill-creator's format:
  - one request the skill should trigger on
  - one near-miss it should not trigger on, such as "audit this repo's READMEs" (that is `/sync-template`, not `sync-from-template`), or "write the session snapshot" (that is `/session-end`, not `docs-updater`)
  - one behaviour case, such as `dependabot` with exactly one qualifying PR proposing direct auto-merge, or `init-project` asking exactly one question per message

  Run them before and after S1, S3 and S4, and note which models ran in the session snapshot.
- **Advantage:** the edits above get evidence that triggering didn't regress, and future skill changes are measured instead of argued.

### 7. S7: Add a "Writing a skill" section to `.claude/skills/README.md`

- **Class / effort / risk:** Patch / S / none.
- **Our gap:** the README covers what earns a slot and how to lay out the folder, but not how to write the file. A new skill (blueprint review K4's `/adr`, for one) would start from scratch.
- **Proposed change:** about ten lines:
  - a link to the guide
  - the limits S5 enforces
  - descriptions say what and when, with trigger phrases first
  - the body holds only what Claude needs to act; maintainer rationale goes in a README
  - instructions that must not be lost go in the first 5,000 tokens
  - scripts are named by repo-relative path
  - three evaluations before merge, run in a fresh session
- **Advantage:** new skills start compliant, rather than being fixed by the next review.

### 8. S8 (optional): A copyable progress checklist in `dependabot`

- **Class / effort / risk:** Patch / S / none.
- **Guide:** for complex workflows, "provide a checklist that Claude can copy into its response and check off as it progresses."
- **Our gap:** `dependabot` has eight phases and a confirmation gate, and no checklist (`init-project` gets one in S3).

## Decisions needed from the maintainer

- **Decision A: should commands set `disable-model-invocation: true`?** This comes from the Claude Code skills page, not the guide, but it follows the guide's first principle that context is shared.
  - **Today:** the descriptions of all seven commands (848 characters) sit in every session's listing, and Claude may start any command on its own, although `.claude/README.md` says commands are "Decided by: You".
  - **With the field:** a command's description leaves the listing, and only the user can start it.
  - **Cost:** `/session-end` Step 3 has Claude run `/commit-msg` (`.claude/commands/session-end.md:54`), and that call would be blocked. Either leave `/commit-msg` model-invocable or inline its steps. `/session-start`'s "offer to run `/session-end`" (`session-start.md:70`) would become "type `/session-end`".
  - **Class:** changing who may start a command is arguably a contract change, which `CHANGELOG.md` classes as Major.
  - **Ordering:** fix the stale "skills cannot be invoked by name" text first (blueprint review K1; still open at `.claude/README.md:69`).
- **Decision B: where should evaluations live?** I recommend inside each skill folder (`evals/evals.json`, skill-creator's default). They cost no context unless read, they document intended behaviour, and a downstream project that customizes a skill can re-run them. The alternative is template-only storage under `docs/template/`, which `init-project` deletes. That keeps downstream folders smaller, but skill-creator would not find the files where it expects them.

## Not recommended

| ID | What | Why |
|---|---|---|
| N1 | Rename the skills to gerund form (`processing-…`) | The guide calls gerunds a "consider". Our noun and action names are among its "acceptable alternatives". A rename changes `/name`, and the old copy would stay downstream as `LOCAL_ONLY`, which sync never removes: a Major change with Migration steps, for no functional gain. Renaming only new skills would create the "inconsistent patterns" the guide warns against. |
| N2 | Rewrite imperative descriptions ("Automate…", "Run…") into third person | The guide's own examples use the imperative. Its warning is about "I" and "you", and no description here uses either. |
| N3 | Restrict frontmatter to the six fields that are portable outside Claude Code | Already the case for skills (`name`, `description`, `compatibility`). Commands use `argument-hint`, but command files are never uploaded. |
| N4 | Tables of contents in reference files | None exist yet. S7 makes it a rule for files over 100 lines once S3 creates some. |
| N5 | Fully qualified MCP tool names | No skill names an MCP tool, and `/roadmap`'s "whatever GitHub tooling this session has" (`roadmap.md:109`) is tool-agnostic on purpose. |
| N6 | Strip the "why" prose throughout | The rationale inside phases is what lets Claude handle cases the steps don't name. Trimming is targeted at text read after the decision is made, or written for maintainers (S3, S4). |
| N7 | Split `dependabot` into reference files | At 389 lines and about 4,400 tokens, it is under both limits, and S4 trims it further. |

## Advantages gained

- **Portability.** Every skill meets the guide's hard limits, so any of them can be uploaded to claude.ai, used through the Skills API, or packaged without editing (S1, S5).
- **Lower standing cost.** About 1,100 fewer characters in every session's skill listing (S1), plus 848 more if Decision A is taken. This happens here and in every downstream project. It matters more than the size suggests: Claude Code's listing has a budget of 1% of the context window, and when it overflows it drops the descriptions of the least-used skills first. A drop like that silently stops a skill from triggering. This session's own listing held over 60 skills.
- **Reliability in long sessions.** `init-project`'s closing gate survives compaction (S3), and `dependabot`'s first script call succeeds (S2).
- **Less context per run.** About 3,400 characters fewer per invocation of `sync-from-template` and `dependabot` (S4), and a Phase-4-only retrofit loads only Phase 4 (S3).
- **Checks instead of reviews.** The limits become a CI failure instead of something a review has to notice (S5), and behaviour becomes measurable, so an edit to a skill is shown not to regress it (S6).
- **A multiplier downstream.** Every project scaffolded from this template inherits `.claude/`, so each fix reaches all of them through `sync-from-template` without Migration steps. Only Decision A would need a Major entry.
- **New skills start right** (S7).

## Suggested follow-on missions

1. **Description and path fixes:** S1, S2, and S4's terminology change. One Patch PR.
2. **Validator:** S5, after or with S1.
3. **`init-project` restructure:** S3.
4. **Body trims and checklist:** S4, S8.
5. **Evaluations:** S6, with Decision B. Run them before missions 3 and 4 land, to get a baseline.
6. **Authoring guide:** S7, last, so it describes what the repo actually does.
7. **Command invocation:** Decision A, together with blueprint review K1.

## Method and limits

- **Sources:** the guide was fetched as raw markdown from its `.md` URL (1,185 lines) and read in full. The Claude Code skills page was fetched the same way for behaviour specific to Claude Code: the 1,536-character listing cap, the 5,000-token re-attach after compaction, `disable-model-invocation`, and the skill-creator eval loop. Where the two disagree, this review says so.
- **Read in full:** all five `SKILL.md` files, all seven command files, both `.claude` READMEs, `validate_skills.sh`, `skills-ci.yml`, `settings.json` and `tooling_paths.txt`. For the bundled scripts, only the headers.
- **Measured, not argued:**
  - description lengths, parsed from the YAML
  - line and character counts
  - the `categorize_prs.py` path failure, run from the repo root
  - the absence of reference files, evaluations, backslash paths and XML in frontmatter

  Token figures are characters ÷ 4. Claude's tokenizer will differ, and for this prose the real count is probably higher, which would move `init-project`'s cut earlier, not later.
- **Not done:** no skill was run or evaluated, so the claims about triggering are untested; S6 is how to test them. No file other than this one was changed.
- **The guide is itself time-sensitive.** Its statement that no built-in eval runner exists is already behind Claude Code's documentation. Re-read both pages before acting on any finding here.
