---
name: dependabot
description: Audit, recommend on, and act on a backlog of open Dependabot pull requests and dependabot/* branches using the GitHub CLI (gh). Gathers each PR's SemVer risk, CI state, merge conflicts, age, security label and release notes; spots superseded duplicates, stale PRs and orphaned branches; cross-checks runtime/base-image bumps against versions pinned elsewhere in the repo; gives a per-PR verdict (merge, consolidate, rebase, close, review, ignore); then carries out only the actions the user approves - consolidating safe Minor/Patch bumps onto one branch, closing superseded PRs, requesting rebases, enabling auto-merge - while always leaving Major bumps and Dependabot's own grouped updates for a human. Use this skill whenever the user mentions Dependabot PRs or branches, dependency bumps, a pile of automated dependency PRs, reviewing or auditing dependency updates, asking what to do about them, consolidating or batching them, or cleaning up the PR queue - even if they don't say "Dependabot" by name.
compatibility: Requires a local git checkout of the target repo, the GitHub CLI (gh) authenticated with repo write access, and Python 3 for the bundled scripts. Designed for an agent runtime with bash tool access, such as Claude Code. Where gh is unavailable, the GitHub MCP tools can stand in for the read-only phases.
---

# Dependabot backlog audit and action

Copy this checklist into your reply and tick it off as you go:

```
- [ ] Phase 0: preflight (gh auth, clean tree; note auto-merge, security alerts)
- [ ] Phase 1: collect open Dependabot PRs and dependabot/* branches
- [ ] Phase 2: classify and score them with the bundled scripts
- [ ] Phase 3: investigate (runtime cross-check, major bumps, security, failing CI)
- [ ] Phase 4: report findings and recommendations (read-only)
- [ ] Phase 5: GATE: the user picks which recommended actions to run
- [ ] Phase 6: execute the approved actions
- [ ] Phase 7: verify before closing anything superseded
```

## Purpose

Dependabot backlogs grow in ways a single "consolidate the safe ones" pass
does not cover: PRs that CI has been failing for weeks, duplicates where a
newer bump replaced an older one, security fixes sitting behind routine
bumps, majors nobody has read the changelog for, and `dependabot/*` branches
whose PRs are long gone. This skill reviews the whole queue, says what it
recommends for each item and why, and then carries out whatever the user
approves.

Most runs end after Phase 4. The audit is the product; actions are opt-in.

## Modes

Pick the mode from the request. When unsure, run the audit and offer actions.

| The user asks to... | Run |
|---|---|
| review, audit, assess, "what should I do about" the PRs | Phases 0-4, then offer Phase 5 |
| consolidate, clean up, "handle" them | Phases 0-7 |
| act on a specific item ("close the superseded ones", "rebase #12") | Phases 0-1 for that item, then 5-7 |

## Non-negotiable constraints

> [!IMPORTANT]
> Never combine or stack two or more Major version bumps into the
> consolidated PR. A Major bump always stays on its own, open, for manual
> review - even if it looks trivial. The skill may *research* a major and
> recommend for or against it; the merge decision stays with the user.

> [!IMPORTANT]
> Never merge anything directly. The only merge-adjacent action this skill
> takes is enabling GitHub's native auto-merge, which still waits for the
> repo's required checks and reviews. It does not bypass CI.

> [!IMPORTANT]
> Nothing in the repo's PR queue or branch list changes before the user
> approves it in Phase 5. Closing a PR, deleting a branch, commenting
> `@dependabot ...`, opening a PR and enabling auto-merge are all visible
> changes. Phases 0-4 are strictly read-only.

> [!IMPORTANT]
> This skill's job is the dependency backlog, nothing more. If a PR's CI
> fails, do not push commits to fix it - even a one-line formatting fix, even
> an issue you're confident is unrelated to the bump. Diagnose it, report it,
> and let the user decide. Fixing unrelated repo issues was never in the plan
> the user approved.

> [!IMPORTANT]
> Never close a superseded or consolidated original until its replacement is
> verified (Phase 7). A PR closed early and then abandoned has no automatic
> way back, so a good update is silently dropped.

## Phase 0: Preflight

Stop and report if a "Must pass" check fails. "Informational" checks never
block; record the result and carry it into the report.

**Must pass:**

1. `gh auth status` succeeds. If not, tell the user to run `gh auth login`
   and stop here.
2. The working tree is clean (`git status --porcelain` prints nothing). If
   not, stop and ask the user to commit or stash first. Phase 6 may switch
   branches and should never carry uncommitted work onto one that could be
   deleted on conflict. (A pure audit never switches branches, but check
   anyway so an approved action doesn't stall later.)

**Informational:**

3. Resolve the default branch:
   ```bash
   DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
   ```
4. Check whether the repo allows auto-merge:
   ```bash
   gh repo view --json autoMergeAllowed -q .autoMergeAllowed
   ```
   The field name has varied across `gh` versions. If it errors, note that
   availability is unknown and will be confirmed when Phase 6 tries it. If
   `false`, say so in the Phase 4 report: any PR will need a manual merge.
5. Read `.github/dependabot.yml` if present: which ecosystems and
   directories are watched, whether `groups`, `ignore`, `open-pull-requests-limit`
   or `commit-message.prefix` are set. An `open-pull-requests-limit` that is
   being hit explains why the queue is stuck; a missing `groups` block
   explains why it is noisy. Both belong in the recommendations.

## Phase 1: Collect

Open PRs, with the fields the audit needs. Use `--limit 100` explicitly:
the default is 30, and a larger backlog silently looks empty past that.

```bash
SCRATCH=$(mktemp -d)
gh pr list --author "app/dependabot" --state open --limit 100 \
  --json number,title,url,headRefName,createdAt,updatedAt,mergeable,mergeStateStatus,reviewDecision,labels,statusCheckRollup \
  > "$SCRATCH/prs.json"
```

> [!NOTE]
> If this returns nothing but the user is sure PRs exist, retry with
> `--author "dependabot[bot]"` - the accepted author string has varied across
> `gh` versions and GitHub Apps configurations. If a field is rejected by an
> older `gh`, drop it; the scripts treat every missing signal as unknown.

If more than 100 PRs come back, say the list may be truncated and offer to
page the rest.

Remote branches, to find orphans:

```bash
git fetch origin --prune
git for-each-ref --format='%(refname:short) %(committerdate:short)' refs/remotes/origin/dependabot/
```

An **orphan** is a `origin/dependabot/*` branch whose name matches no open
PR's `headRefName`. Dependabot normally deletes these itself, so a few mean
something went wrong (a PR closed by hand, a failed run).

If there are no open PRs *and* no `dependabot/*` branches, respond exactly:

```
No open Dependabot PRs found. Exiting.
```

Stop here in that case.

## Phase 2: Classify and score

Pipe the JSON through both scripts, from the repo root:

```bash
python3 .claude/skills/dependabot/scripts/categorize_prs.py < "$SCRATCH/prs.json" \
  | python3 .claude/skills/dependabot/scripts/audit_prs.py > "$SCRATCH/audit.json"
```

Use the scripts rather than judging titles, versions or check results by
eye. Neither touches git, GitHub or the network.

`categorize_prs.py` assigns `category` (it only reads the title):

- `Major` - includes a pre-1.0 *minor* bump (`0.4.x` to `0.5.x`), since
  SemVer promises nothing below 1.0.
- `Minor/Patch` - the package's own SemVer promise only; Phase 3 checks
  whether this repo can tolerate it.
- `Grouped` - Dependabot's own grouped update. Left intact: it was tested as
  a combination, and picking it apart forfeits that.
- `Unknown` - an unrecognised title, an unparseable version, or a
  requirement-range widening (`Update mcp requirement from <2,>=1.28.1 to
  >=1.28.1,<3`) with no single old/new pair. Never guess a risk level.

It handles GitHub Actions `v3` style tags and strips a Conventional-Commits
prefix such as `chore(deps): `.

`audit_prs.py` adds `ci`, `conflict`, `behind`, `age_days`, `security`,
`superseded_by`, `ecosystem`, `directory`, `signals`, and a `recommendation`:

| `recommendation` | Meaning | Typical action |
|---|---|---|
| `merge-candidate` | Minor/Patch, clean, CI green or absent | consolidate, or auto-merge if alone |
| `wait` | Minor/Patch, CI still running | revisit; do not act yet |
| `rebase` | Minor/Patch, conflicting or behind base | `@dependabot rebase` |
| `investigate-ci` | Minor/Patch, CI failing | diagnose and report (Phase 3) |
| `close-superseded` | A newer open PR bumps the same package further | close with a pointer |
| `review-major` | Major or pre-1.0 minor | research, then the user decides |
| `review-grouped` | Dependabot's own group | review whole; merge or leave |
| `manual-review` | Not classifiable | a human reads it |

The recommendation is a starting point, not a verdict. Phase 3 can overturn it.

## Phase 3: Investigate

Do this only for the items that need it, and say what you checked. With many
PRs, work the highest-risk ones first: security, then majors, then failing CI.

**Runtime and base-image bumps (`merge-candidate` only).** `Minor/Patch`
describes the package's promise, not whether this repo tolerates the change.
For a language runtime or Docker base image (`python`, `node`, `ruby`, any
`-slim` / `-alpine` tag), search for conflicting pins:

```bash
grep -rn -E "python[_-]?version|target-version|pythonVersion|FROM python" \
  --include='*.toml' --include='*.md' --include='Dockerfile*' \
  --include='.python-version' .
```

Adjust the pattern for the runtime (`node`/`.nvmrc`, `ruby`/`.ruby-version`,
`.tool-versions`, CI workflows that hardcode a version). If a pin would be
violated, downgrade the PR to `manual-review` and name the file and setting,
for example: "conflicts with `pyproject.toml`'s `ruff target-version =
\"py312\"`". The grep only catches what a grep can; when you are not
confident it was thorough, lean toward `manual-review`.

Ordinary libraries and GitHub Actions don't need this check.

**Security (`security: true`).** A security PR outranks every routine bump,
including ahead of an older, quieter queue. Look up what it fixes:

```bash
gh pr view <NUM> --json body -q .body
```

Dependabot's PR body names the advisory (GHSA/CVE) and severity. Report
those. If a security PR is also `review-major`, say so prominently: it is the
case where waiting has a cost, and the user should hear it first.

**Major bumps (`review-major`).** The aim is to let the user decide in a
minute, not to make the decision. For each:

1. Read the release notes and changelog in the PR body (`gh pr view <NUM>
   --json body -q .body`), looking for removed or renamed APIs, dropped
   runtime versions and changed defaults.
2. Check whether the repo uses the affected surface at all:
   `grep -rn "<package>" --include=...`. A major bump of a library imported
   in one test file is a different risk from one imported in forty modules.
3. Check CI: a green run on a major raises confidence but does not close the
   question, because CI only covers what the tests cover.
4. Give a call: **low-risk, probably just merge** / **needs a migration
   (name it)** / **not worth it yet** - with the evidence. If evidence is
   thin, say "could not determine" rather than guessing.

**Failing CI (`investigate-ci`).** Find out whether the failure comes from
the bump or was already there:

```bash
gh pr checks <NUM>
gh run view <RUN_ID> --log-failed | head -80
```

Compare with the default branch's latest run. If the default branch is red
too, the failure is not the PR's and the answer is "fix the base first". If
only this PR fails, name the test and the likely cause. Do not push a fix.

**Superseded (`close-superseded`).** Confirm that the superseding PR is open
and is not itself a failing or conflicting one - closing a good-but-older PR
in favour of a broken newer one loses the working option. If the newer one is
broken, say so and recommend keeping the older.

**Stale (`signals` containing `open Nd`).** A Dependabot PR open for more
than ~45 days has usually been passed over on purpose or forgotten. For each,
ask which it is: if it is a major nobody wants, recommend closing with
`@dependabot ignore this major version`; if it is just unreviewed, say so.

**Orphan branches.** For each, check the last commit date and whether the
branch has any commits beyond the default branch
(`git log origin/$DEFAULT_BRANCH..origin/<branch> --oneline`). An orphan with
no PR is safe to propose for deletion; one with unmerged non-Dependabot
commits is not - flag it instead.

**Config observations.** From Phase 0 step 5, note things that would reduce
the backlog at the source: no `groups` block, ecosystems with no coverage,
an `open-pull-requests-limit` being hit, an `ignore` rule that is stale.
Recommend them as `.github/dependabot.yml` changes, but make no edits here -
that is a separate change the user can ask for.

## Phase 4: Report

Present the findings read-only. Lead with what matters, not with a table of
everything. Order: security items, then anything blocking or broken, then the
routine bulk.

```markdown
## Dependabot audit: <repo> - <N> open PRs, <M> orphan branches

**Needs attention first**
- #41 (security, HIGH) pillow 10.1 to 10.3 - fixes GHSA-xxxx; CI green. Recommend: merge now.
- #37 (security) django 4.2 to 5.0 - Major. Fixes CVE-xxxx. Release notes drop Python 3.9; repo pins 3.12, so fine. Recommend: merge after a manual look.

**Recommended actions**
| # | Package | Change | Category | CI | Recommendation | Why |
|---|---------|--------|----------|----|----------------|-----|
| 52 | requests | 2.30 to 2.31 | Minor/Patch | pass | consolidate | clean |
| ... | | | | | | |

**Leave open for a human:** #44 (react 17 to 18 - Major; ...)
**Stuck:** #39 (CI failing on `test_parser`; default branch is green, so this PR's)
**Orphan branches:** dependabot/pip/old-1.2 (last commit 2026-04-01, no PR)
**Config:** no `groups` block, so each patch opens its own PR...
**Auto-merge:** repo setting is off; merges will be manual.
```

Keep every claim traceable: say "could not determine" for anything you did
not check. State what happened, not what might have happened.

If nothing qualifies for any action, say so plainly and stop.

## Phase 5: Confirmation gate

> [!IMPORTANT]
> Do not proceed until the user confirms. End the report with the concrete
> actions available, numbered, and ask which to run. Example:

```
Actions I can take - reply with numbers, "all", or tell me what to change:
  1. Consolidate #52, #53, #55 onto one branch and PR (3 Minor/Patch)
  2. Enable auto-merge on #41 (security; CI green)
  3. Close #48 and #50 as superseded by #51
  4. Comment "@dependabot rebase" on #39
  5. Delete 2 orphan branches
Not offered: #44 and #37 (Major) - your call after reading the notes above.
```

An instruction such as "run this end to end" or "just do it" given before
the audit counts as approval for the actions the audit recommends, but never
for Major bumps, which are always the user's call. When in doubt, gate it.

Replying "consolidate" approves action 1 alone.

## Phase 6: Execute the approved actions

Run only what was approved, one action at a time, reporting each result.

### Consolidate Minor/Patch bumps

With exactly one `merge-candidate`, consolidating adds nothing - it closes a
PR and reopens the identical change under a new number. Enable auto-merge on
it directly (`gh pr merge <NUM> --auto --squash`), or leave it for a manual
merge if the repo disallows auto-merge, and skip the rest of this section.

With two or more:

```bash
TIMESTAMP=$(date +%s)
BRANCH="chore/consolidate-dependabot-updates-${TIMESTAMP}"
git fetch origin "$DEFAULT_BRANCH"
git switch -c "$BRANCH" "origin/$DEFAULT_BRANCH"
```

For each included PR, in ascending PR number:

```bash
git fetch origin "pull/${NUM}/head"
BASE=$(git merge-base HEAD FETCH_HEAD)
git cherry-pick "${BASE}..FETCH_HEAD"
```

Cherry-picking the range handles the rare multi-commit Dependabot PR while
applying only that PR's own changes.

**On any conflict:** `git cherry-pick --abort`, switch back to
`$DEFAULT_BRANCH`, `git branch -D "$BRANCH"`, and tell the user which package
conflicted. Do not resolve it or skip that PR and continue - the batch was
approved as a whole, and nothing has been pushed, so the originals are
untouched.

```bash
git push -u origin "$BRANCH"
PR_URL=$(gh pr create --base "$DEFAULT_BRANCH" --head "$BRANCH" \
  --title "chore: consolidate N safe Dependabot updates" --body "$CONSOLIDATION_BODY")
NEW_PR_NUMBER=$(basename "$PR_URL")
gh pr merge "$NEW_PR_NUMBER" --auto --squash
```

`CONSOLIDATION_BODY` lists the included PRs (number, package, version change)
so the new PR traces back to what it replaces. If auto-merge fails because
the repo disallows it, that is not fatal; note "manual merge required". Any
other `gh pr create` / `gh pr merge` failure (branch protection, required
reviews): report the exact error and stop.

**Do not close any original here.** See Phase 7.

### Other actions

- **Enable auto-merge on a single PR:** `gh pr merge <NUM> --auto --squash`.
  Only for a `merge-candidate` or an approved security PR with green CI.
- **Close a superseded PR** (the replacement must be open and healthy per
  Phase 3): `gh pr close <NUM> --comment "Superseded by #<NEWER>."`
- **Request a rebase:** `gh pr comment <NUM> --body "@dependabot rebase"`.
  If a PR is badly conflicted, `@dependabot recreate` rebuilds it from
  scratch, but discards any manual edits to it, so use it only when the
  user approves that specifically.
- **Ignore a dependency or major version** (a user decision about a specific
  PR, never inferred): `gh pr comment <NUM> --body "@dependabot ignore this major version"`
  (or `ignore this minor version`, `ignore this dependency`), then close with
  a comment saying why. Dependabot records the ignore, so the PR does not come
  back.
- **Delete orphan branches:** `git push origin --delete <branch>`, one at a
  time, each only if Phase 3 found no unmerged non-Dependabot commits.

Any `gh` error: report the exact message and stop that action. Do not retry
by a different route that goes beyond what the user approved.

## Phase 7: Verify before closing consolidated originals

```bash
gh pr checks "$NEW_PR_NUMBER"
```

- **CI green, and no automated reviewer has an unresolved objection:** close
  each original that actually made it into the branch:
  `gh pr close "$NUM" --comment "Superseded by consolidated PR #${NEW_PR_NUMBER}."`
  A PR that was left out stays open - it was never superseded.
- **CI still running:** don't block the session. Use a scheduled follow-up if
  the runtime supports one; otherwise report that closure is pending and
  needs a re-check. Leave the originals open meanwhile.
- **CI fails:** do not push a fix. Report it plainly, say whether it looks
  related to the bump or pre-existing, leave the originals open, and ask how
  to proceed (fix and retry, close the consolidated PR, or case by case).
- **An automated reviewer raises a substantive objection** (for example a
  version now conflicting with something pinned elsewhere): treat it like a
  CI failure. Surface it and get a decision before closing anything.

## Output format

After acting, report using only the lines that apply:

```markdown
- **Consolidated PR Created:** #102 (chore/consolidate-dependabot-updates-1715000000) - *Auto-merge enabled*
- **Auto-merge Enabled Directly:** #41 (pillow 10.1 to 10.3, security) - *no consolidation branch; only one qualified*
- **PRs Closed:** #98 (setup-buildx-action), #99 (python-runtime)
- **Closed as Superseded:** #48, #50 (by #51)
- **Rebase Requested:** #39
- **Branches Deleted:** dependabot/pip/old-1.2
- **PRs Pending Closure:** #4 (python 3.12-slim to 3.14-slim) - closes once #102's CI is green
- **PRs Left Open:** #97 (setup-qemu-action v2 to v3 - Major; needs review)
- **Needs Your Decision:** #102 - CI failed on "Lint, format, test"; not auto-fixed (out of scope). Originals left open.
```

When the run was an audit only, the Phase 4 report is the output; end by
restating the numbered actions still available.

## Tone

Professional, cautious, and exact. The reader is the engineer who invoked the
skill and will act on what it reports - state what happened and what you
verified, and separate that from what you inferred.
