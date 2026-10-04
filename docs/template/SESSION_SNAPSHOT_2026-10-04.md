## Session Goals
Two missions. Mission 6: explore gitlab.com/macrodream/blueprint for ways to improve
the template, delivering a ranked review. Mission 3 (extended, chosen as "option 2"
after the review failed the scaffold smoke test): stop the template's own records
leaking into scaffolded projects, so the review could live in the repo.

## Accomplishments
- Blueprint review (docs/template/blueprint-review.md, 198 lines). Pinned to blueprint
  commit b272f45. 40 candidates filtered through scope, forge-only, downstream-cost
  and already-covered tests plus a no-evidence-of-harm tie-break: 14 kept (13 firm,
  1 optional), 5 deferred with revisit triggers, 21 dropped with reasons, 1 observation.
  All 70 citations checked mechanically; no verbatim reuse (Apache-2.0 vs MIT).
- Findings about our own repo, each measured rather than argued: the "skills cannot be
  invoked by name" premise is stale (README.md:12 contradicts .claude/README.md:69;
  the docs say commands merged into skills); deleting the only SessionStart wiring
  left every check green; CI runs shellcheck but CONTRIBUTING.md's list omits it;
  GitHub has no tags or releases so changelog links point at nothing; the hook test
  merges stdout and stderr; nothing scans for secrets.
- Template-records leak fixed (branch fix/template_records_leak). New docs/template/
  (README, the two old snapshots moved with git mv, the review); this repo's
  SNAPSHOT_PATH points there. check_scaffolded_project.sh reports the folder, or a
  SNAPSHOT_PATH inside it, as TEMPLATE_RESIDUE (6 cases, mutation-checked, including a
  guard that a project's own snapshots stay clean). check_inherited_docs.sh skips the
  folder (3 cases). simulate_init.sh and init-project Phase 3 delete it and reset
  SNAPSHOT_PATH, first scaffold only, so the retrofit path never touches a project's
  history. CONTRIBUTING.md and CHANGELOG [Unreleased] updated.
- Verified: 8 gate scripts (verifier 24/24, sweep 21/21), ruff, 62 pytest tests,
  shellcheck on 14 scripts (installed outside the repo; it caught an SC2016 in my
  first edit of simulate_init.sh), both simulated scaffolds PROBLEMS=0 with the review
  present, repo sweep unchanged at 16.
- Local checkpoint commit ec9eaec (steps 2-6) made on request; not pushed.

## Technical Debt / Pending
- Two decisions only the maintainer can make: Decision A (create tags and releases
  for v1.0.0 to v2.1.0, or point the changelog links elsewhere) and Decision B
  (secret-scanning mechanism: scanner binary, vendor action, or GitHub's built-in).
- The review's 13 kept items (K1 to K13) are not started; grouped into six follow-on
  missions in its "Suggested follow-on missions" section.
- Existing projects may still hold the two inherited template snapshots; noted in
  CHANGELOG, deliberately not a migration step.
- The delete list is mirrored by hand in simulate_init.sh, init-project's SKILL.md and
  the verifier. Parity was checked once, manually, with a scratchpad script. A
  permanent check belongs to the review's K2 mission.
- TEST_COMMAND / LINT_COMMAND remain placeholders by design; the working gate is
  CONTRIBUTING.md's list, which still lacks shellcheck (review item K3).
- Local environment: ruff 0.15.20 vs the 0.16.8 pin; python3 -m pytest unavailable
  (use pytest); shellcheck lives in a scratchpad venv and is gone next session.
- PRs #26 (ruff 0.16.9) and #20 (setup-python 5 to 7) were open at session start and
  untouched.

## Next Steps
- Review and merge fix/template_records_leak; open a PR only when asked.
- Cut release 2.2.0: move [Unreleased] to a version, bump .template-version, add the
  missing link references. Settle Decision A first.
- Then the review's follow-on missions, in its order: docs and config truth (K1 K3
  K8 K9 K10 K12), wiring and registration checks (K2a K2b K6), gate and test-writing
  rules (K5 K13), /adr (K4), release state (K7), secret scanning (K11 plus Decision B).
- Triage the two Dependabot PRs.
