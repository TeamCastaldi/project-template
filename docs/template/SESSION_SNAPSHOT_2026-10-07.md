## Session Goals
Review Anthropic's skill authoring best-practices guide against this template, turn
the findings into a phased plan, then implement every phase as its own pull request,
each green in CI before the next began.

## Accomplishments
- Review (docs/template/skill-best-practices-review.md): 8 changes worth doing (S1–S8),
  2 decisions, 7 items deliberately not adopted (N1–N7). Measured, not argued: two
  descriptions over the 1,024-character limit (init-project 1,307, sync-from-template
  1,302); init-project's ~7,400 tokens past Claude Code's 5,000-token post-compaction
  window; dependabot's script command failing from the repo root (exit 2).
- Plan (docs/template/skill-best-practices-plan.md): ten phases, a concern tracker,
  runnable verification per phase. Decisions recorded: commands set
  disable-model-invocation: true, with /commit-msg left model-invocable (A); evaluations
  live in each skill folder (B).
- Ten stacked pull requests, each green in CI: #29 review and plan, #30 script paths,
  #31 three evaluations per skill, #32 descriptions under 1,024, #33 validate_skills.sh
  enforces the guide's limits (33-case test, mutation-checked), #34 init-project split
  into references/ with a top-of-file checklist (28,867 to ~18,900 characters), #35
  dependabot and sync-from-template trims plus a dependabot checklist, #36 "Writing a
  skill" rules, #37 six commands no longer start on their own and the stale "skills
  cannot be invoked by name" text fixed (blueprint K1), then the close-out.
- Downstream check: a project scaffolded from main receives every .claude/ and
  synced-script change on sync (9 NEW, 16 CHANGED). The two edits outside sync's reach
  (.gitignore, skills-ci.yml) are now CHANGELOG migration steps.

## Technical Debt / Pending
- The 15 evaluations have never been run. They need skill-creator in a local session;
  docs/template/skill-eval-baseline.md is empty.
- Phase 8's behaviour checks need a fresh local session: Claude suggests /session-end
  instead of running it; /session-end still drafts through /commit-msg; the Skills row
  in /context shrinks.
- Release 3.0.0 is not cut. .template-version stays 2.1.0 until it is.
- Blueprint review K2b would remove the five-place manual registration Phase 4 needed
  for test_validate_skills.sh.

## Next Steps
1. Merge #29, then #30 to #37, then the close-out, in that order.
2. Run the evaluations per .claude/skills/README.md → Evaluations, and fill in
   skill-eval-baseline.md, one table per model family.
3. Run Phase 8's three checks in a fresh session.
4. Cut 3.0.0: date the Unreleased section, add its link reference, set .template-version.
