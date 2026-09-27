## Session Goals
Build a roadmap management command matching the repo's existing artifact patterns
(init, evaluate, add/update, complete), strictly grounded in the codebase, issues and
stated goals. Follow-up: make /sync-from-template carry the scripts .claude/ commands
depend on, and resolve PR #24's merge conflict with main (2.1.0).

## Accomplishments
- `/roadmap` command (.claude/commands/roadmap.md): menu + four operations, each write
  behind an exact gate phrase. Grounding rules: every item cites a repo path, an open
  issue, or an explicit request; restate sources at their own scope; "done" needs
  pointable evidence; add/complete change exactly one line, proven with git diff.
- scripts/check_roadmap.sh: read-only checklist parser — OPEN/BLOCKED/DONE inventory
  with line and section; flags NO_SOURCE, BROKEN_SOURCE, MAYBE_DONE, DONE_MISSING.
  32 tests; mutation-checked. Wired into skills-ci.yml, settings.json allow rules,
  scripts/README.md, CONTRIBUTING.md.
- ROADMAP_PATH (docs/plans/ROADMAP.md) added to CLAUDE.md Session Config; /roadmap
  falls back to the same default when the row is absent.
- .claude/README.md gained the command/skill/hook index /sync-template item 2 already
  expected (13 entries after merging main).
- sync-from-template: tooling_paths.txt lists the 4 scripts outside .claude/ that
  commands/skills run (+ tests); compare_template.sh reads it from the template commit
  and now accepts single-file sync paths (previously a fatal exit 128). 10 new tests.
  Verified end to end with a two-pass upgrade sync into a downstream copy.
- Bug found by trial run and fixed: /roadmap init dropped in-progress items whose
  stub file already existed; it now opens the file first, as evaluate does.
- Merged origin/main (2.1.0: testing-standards, /audit-tests) into the branch. Resolved
  CHANGELOG conflict (branch entries stay under [Unreleased], above [2.1.0]) and added
  the two new artifacts to the index.

## Technical Debt / Pending
- PR #24's title still names only the first commit (check_roadmap.sh); the branch now
  also carries /roadmap and the sync-from-template tooling change.
- CHANGELOG link refs at the bottom stop at [2.0.0]; main's 2.1.0 release added no
  [2.1.0] link and [Unreleased] still compares from v2.0.0.
- check_inherited_docs.sh reports 16 in this repo (was 15): the new hit is main's own
  2.1.0 testing-standards entry (CHANGELOG.md:50). Template-repo noise, not CI.
- Snapshots written in this repo ride along into every scaffolded project: nothing in
  init-project removes docs/session-history/SESSION_SNAPSHOT_*. The first draft of this
  file quoted a phrase the sweep flags, which failed check_scaffolded_project.sh in the
  scaffold simulation — caught by the session-end gate, reworded, not yet fixed at root.
- sync-from-template's description is ~1,300 chars; some Claude Code versions cap
  descriptions at 1,024. Loads fine here, but worth trimming.
- A downstream project that pulls the new test scripts won't run them in CI until its
  skills-ci.yml gains the steps — deliberately not synced.
- TEST_COMMAND / LINT_COMMAND remain placeholders here by design (simulate_init.sh
  fills them); the working gate is the CONTRIBUTING.md check list.

## Next Steps
- Retitle/re-describe PR #24 to cover the whole branch, then merge once CI is green.
- On release: move [Unreleased] to a version (Minor → 2.2.0), bump .template-version,
  and fix the CHANGELOG link refs (add [2.1.0], [2.2.0]).
- Optionally trim sync-from-template's description under 1,024 chars.
- In a real downstream project, run /sync-from-template twice (old compare script
  first), then /roadmap init.
