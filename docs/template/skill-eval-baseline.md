# Skill evaluation baseline

Status: **cases written, not yet run.** Phase 2 of [`skill-best-practices-plan.md`](skill-best-practices-plan.md) added three evaluations per skill (`.claude/skills/<name>/evals/evals.json`). Running them needs a local Claude Code session with the skill-creator plugin. The cloud session that wrote them could not install the plugin, so no numbers are recorded yet. How to run them, and the setup each case needs, is in [`.claude/skills/README.md`](../../.claude/skills/README.md#evaluations).

As of the close-out (2026-10-07) they are still not run, and Phases 3, 5 and 6 are written, so the first run will be on the changed text. Record it here as the baseline anyway, and say so in the notes.

This baseline was meant to be taken **before** Phase 3 lands. Phases 3, 5 and 6 change skill text. If they merge first, run their skills' cases on the merged text as well, and say so in the notes.

## How to record a run

One table per model family. Each cell shows assertions passed out of assertions total, with the skill and without it, for example `4/4 · 1/4`. For a near-miss case (case 2), the score that matters is the one with the skill available: the skill should not trigger, so a pass there means it stayed out of the way.

## Results

### Model family: _not run_

| Skill | 1 trigger | 2 near-miss | 3 behaviour | Notes |
|---|---|---|---|---|
| `dependabot` | not run | not run | not run | |
| `docs-updater` | not run | not run | not run | |
| `init-project` | not run | not run | not run | |
| `sync-from-template` | not run | not run | not run | |
| `testing-standards` | not run | not run | not run | |

Copy the table for each further model family. Phase 9 adds final numbers beside these.
