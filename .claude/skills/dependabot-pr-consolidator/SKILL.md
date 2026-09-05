---
name: dependabot-pr-consolidator
description: Automate triage and safe consolidation of open Dependabot pull requests in a Git repository using the GitHub CLI (gh). Categorizes each open Dependabot PR by SemVer risk (Major, Minor/Patch, Grouped, or Unknown), bundles the safe Minor/Patch bumps onto one consolidated branch and PR with auto-merge enabled, and closes the superseded originals - while always leaving Major version bumps and Dependabot's own grouped updates open for manual review. Use this skill whenever the user mentions Dependabot PRs, dependency bumps, consolidating or batching dependency updates, cleaning up a repo's open PR queue, or asks to triage, merge, or close a pile of automated dependency pull requests - even if they don't say "Dependabot" by name.
compatibility: Requires a local git checkout of the target repo, the GitHub CLI (gh) authenticated with repo write access, and Python 3 for the bundled categorization script. Designed for an agent runtime with bash tool access, such as Claude Code.
---

# Dependabot PR consolidator

## Purpose

Open Dependabot PRs pile up fast. Most are low-risk minor or patch bumps
that are safe to batch together. Some are major version bumps that need a
human to read the changelog. This skill sorts the pile, merges what is
safe into one PR, and leaves the rest open with a clear reason.

## Non-negotiable constraints

> [!IMPORTANT]
> Never combine or stack two or more Major version bumps into the
> consolidated PR. A Major bump always stays on its own, open, for manual
> review - even if it looks trivial.

> [!IMPORTANT]
> Never merge anything directly. This skill only creates the consolidated
> PR, enables GitHub's native auto-merge on it, or closes a superseded PR.
> Auto-merge still waits for the repo's required status checks and
> reviews before it merges anything - it does not bypass CI.

## Phase 0: Preflight

Run these checks before reading any PRs. Stop and report if any fails.

1. Confirm `gh auth status` succeeds. If it does not, tell the user to run
   `gh auth login` and stop here.
2. Confirm the local working tree is clean (`git status --porcelain`
   prints nothing). If it is not, stop and ask the user to commit or
   stash their changes first. This skill creates and switches branches,
   and it should never risk carrying the user's uncommitted work onto a
   branch that later gets deleted on conflict.
3. Resolve the repo's default branch:
   ```bash
   DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
   ```

## Phase 1: Query open Dependabot PRs

```bash
gh pr list --author "app/dependabot" --state open \
  --json number,title,url,headRefName --limit 100
```

Use `--limit 100` explicitly. The default limit is 30, and a repo with a
larger backlog will silently look empty past that.

> [!NOTE]
> If this returns nothing but the user is sure PRs exist, retry with
> `--author "dependabot[bot]"` - the accepted author string has varied
> across `gh` versions and GitHub Apps configurations.

If the query returns an empty list, respond exactly:

```
No open Dependabot PRs found. Exiting.
```

Stop here in that case. Do not proceed to later phases.

## Phase 2: Categorize each PR by SemVer risk

Pipe the JSON from Phase 1 into the bundled script:

```bash
gh pr list --author "app/dependabot" --state open \
  --json number,title,url,headRefName --limit 100 \
  | python3 scripts/categorize_prs.py
```

Use the script rather than eyeballing version numbers. Two cases are easy
to get wrong by hand and the script handles both:

- A pre-1.0 package (`0.x.y`) has no stability guarantee below `1.0`, so
  SemVer treats a change in the minor number the same as a major bump
  elsewhere. `0.21.4 -> 0.22.0` is flagged `Major`, not `Minor/Patch`.
- GitHub Actions are commonly tagged `v2`, `v3` rather than `2.0.0`. The
  script strips the leading `v` before comparing.

The script returns four categories per PR: `Major`, `Minor/Patch`,
`Grouped`, or `Unknown`. See the script's docstring
(`scripts/categorize_prs.py`) for the full rule set.

`Grouped` PRs are Dependabot's own grouped-update PRs (its title matches
"Bump the `<group>` group ... with `N` updates"). Leave these alone
rather than decomposing them - Dependabot already tested that combination
of packages together, and picking it apart forfeits that guarantee.

`Unknown` PRs are anything the script could not confidently parse. Route
these to manual review. Never guess a risk level for a title or version
string the script did not recognize.

## Phase 3: Build the consolidation plan

From the categorized list, build a plan:

- **Include** every `Minor/Patch` PR.
- **Leave open** every `Major`, `Grouped`, and `Unknown` PR, each with its
  `reason` from the script.

Present this plan to the user as a short table or list before touching
any repository state - PR number, package, version change, category, and
what will happen to it. This is the point to catch anything that looks
off before Phase 4 starts making changes.

If no PR qualifies for `Minor/Patch`, say so plainly, list every PR under
"left open" with its reason, and stop. Do not create an empty
consolidated PR.

## Phase 4: Confirmation gate

> [!IMPORTANT]
> Do not proceed past this point until the user confirms. Phases 5-7
> create a branch and a PR, enable auto-merge, and close other PRs -
> all real, visible changes to the repo's PR queue. Show the plan from
> Phase 3, then ask the user to reply **"consolidate"** to proceed, or
> tell you what to change.

Skip this gate only if the user's own request already made unattended
execution explicit (for example, "run this end to end, no need to check
in" or an equivalent instruction given before this skill started). When
in doubt, gate it.

## Phase 5: Build the consolidated branch

```bash
TIMESTAMP=$(date +%s)
BRANCH="chore/consolidate-dependabot-updates-${TIMESTAMP}"
git fetch origin "$DEFAULT_BRANCH"
git switch -c "$BRANCH" "origin/$DEFAULT_BRANCH"
```

For each included PR, in ascending PR number order (deterministic, and
matches the order Dependabot opened them):

```bash
git fetch origin "pull/${NUM}/head"
BASE=$(git merge-base HEAD FETCH_HEAD)
git cherry-pick "${BASE}..FETCH_HEAD"
```

Cherry-picking the commit range (not just the tip commit) handles the
rare Dependabot PR with more than one commit, while still applying only
that PR's own changes.

**On any conflict** (per the edge case below): abort immediately. Do not
try to resolve it, skip the offending PR, and continue with the rest -
the whole batch was presented to the user as one plan in Phase 3, so
partially applying it would ship something they did not approve.

## Phase 6: Open the consolidated PR and enable auto-merge

```bash
git push -u origin "$BRANCH"
PR_URL=$(gh pr create \
  --base "$DEFAULT_BRANCH" \
  --head "$BRANCH" \
  --title "chore: consolidate N safe Dependabot updates" \
  --body "$CONSOLIDATION_BODY")
NEW_PR_NUMBER=$(basename "$PR_URL")
gh pr merge "$NEW_PR_NUMBER" --auto --squash
```

Build `CONSOLIDATION_BODY` as a short list of the included PRs (number,
package, version change) so the consolidated PR is traceable back to the
originals it replaces.

## Phase 7: Close superseded PRs

For every PR that was actually included in Phase 5:

```bash
gh pr close "$NUM" --comment "Superseded by consolidated PR #${NEW_PR_NUMBER}."
```

Only close PRs that made it into the consolidated branch. A PR left open
in Phase 3 stays open - it was never superseded.

## Edge cases

- **No Dependabot PRs found**: respond exactly `No open Dependabot PRs
  found. Exiting.` and stop (Phase 1).
- **Working tree not clean**: stop before Phase 1 and ask the user to
  commit or stash first (Phase 0).
- **GitHub CLI not authenticated**: instruct the user to run
  `gh auth login` and stop execution (Phase 0).
- **Git conflict while cherry-picking**: abort the cherry-pick
  (`git cherry-pick --abort`), switch back to `$DEFAULT_BRANCH`, delete
  the temporary branch (`git branch -D "$BRANCH"`), and tell the user
  which package's PR conflicted. Nothing has been pushed or closed at
  this point, so the original PRs are untouched and safe to retry
  individually.
- **`gh pr create` or `gh pr merge` fails** (for example, branch
  protection blocks auto-merge, or required reviews are missing): report
  the exact `gh` error to the user. Do not close any original PRs - they
  are only superseded once the consolidated PR actually exists.

## Output format

On completion, report using this exact structure:

```markdown
- **Consolidated PR Created:** #102 (chore/consolidate-dependabot-updates-1715000000) - *Auto-merge enabled*
- **PRs Closed:** #98 (setup-buildx-action), #99 (python-runtime)
- **PRs Left Open:** #97 (setup-qemu-action v2 to v3 - Major bump)
```

If no PRs qualified for consolidation (Phase 3), skip the first line and
report only what was left open and why.

## Tone

Professional, cautious, and exact. The person reading this is the
engineer who invoked the skill and will act on what it reports -
state what happened, not what might have happened.

## Bundled script

`scripts/categorize_prs.py` - reads a JSON array of PRs from stdin
(the shape `gh pr list --json number,title,url,headRefName` produces)
and prints the same array back with `package`, `old_version`,
`new_version`, `category`, and `reason` added to each entry. Pure
classification - it never touches git or the network. Run it directly
against synthetic input to sanity-check its rules before trusting it
against a real PR queue.
