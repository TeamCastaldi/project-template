# Skill evaluation baseline

Status: **one spot check recorded (`docs-updater`, Opus 5.5); the other four skills not yet run.** Phase 2 of [`skill-best-practices-plan.md`](skill-best-practices-plan.md) added three evaluations per skill (`.claude/skills/<name>/evals/evals.json`). Running them needs a Claude Code session with the skill-creator plugin. How to run them, and the setup each case needs, is in [`.claude/skills/README.md`](../../.claude/skills/README.md#evaluations).

The cloud session that wrote the cases did not run them. An earlier version of this page said it could not install the plugin; it never tried.

This baseline was meant to be taken **before** Phase 3 landed. Phases 3, 5 and 6 merged first, so every run recorded here is on their changed text, and the notes say so.

## How to record a run

One table per model family. Each cell shows assertions passed out of assertions total, with the skill and without it, for example `4/4 · 1/4`. For a near-miss case (case 2), the score that matters is the one with the skill available: the skill should not trigger, so a pass there means it stayed out of the way.

## Results

### Model family: Opus 5.5

| Skill | 1 trigger | 2 near-miss | 3 behaviour | Notes |
|---|---|---|---|---|
| `dependabot` | not run | not run | not run | |
| `docs-updater` | 3/4 · 2/4 | 2/2 · 2/2 | 4/4 · 4/4 | Spot check, 2026-10-07, on cases that have since changed. The comparison is flawed; see below. |
| `init-project` | not run | not run | not run | |
| `sync-from-template` | not run | not run | not run | |
| `testing-standards` | not run | not run | not run | |

Copy the table for each further model family.

#### `docs-updater`, 2026-10-07

Record the next run beside this one, not in its place.

- **One run per case and configuration.** The benchmark's header says 3 runs; it was one.
- **The runs without the skill could still see it.** skill-creator removed the skill by deleting its files, but the project had been committed to git first, so the files were still in its history. Two of the runs noticed the deletion. The how-to now turns the skill off with `skillOverrides` instead.
- **Case 1 could not pass as written.** The project had no export code, so with the skill Claude rightly declined to document one, and the full-README-replacement check failed. Without the skill, the "skill is invoked" check also fails, as it always will.
- **Cases 2 and 3 scored the same either way, but the outputs differed where no check looked.** Without the skill, case 2 wrote the snapshot file itself and case 3 wrote its edits straight to disk. With it, case 2 pointed the user at `/session-end` and case 3 proposed its edits.
- **The cases and the skill changed after this run.** Case 1 gained a fixture with real export code and a check that the documented syntax matches it; cases 2 and 3 each gained a check for the difference above. The skill gained a rule on what counts as evidence. Later scores are out of different totals, so compare outputs, not numbers.
- skill-creator's review viewer showed "(No prompt found)" above each output. That is the run's metadata, not the cases.
