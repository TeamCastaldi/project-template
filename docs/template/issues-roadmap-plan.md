# Issue tracking on GitHub Issues — decisions

**Date:** 2026-10-08 · **Status:** implemented on `claude/trusting-mendel-hlzyc7`, not yet released (3.0.0)

The file-based `/roadmap` (a markdown checklist at `ROADMAP_PATH`, checked by `check_roadmap.sh`) was replaced, before it ever shipped in a release, by planned work kept as GitHub Issues. This records what was decided and why, so a later change can tell a deliberate choice from an accident.

## The goal

A user should be able to work with the repo's issue tracker **in conversation** — note a bug or an idea mid-session, pick it up in a fresh one — and it should **work in a new repo with no setup**: `init-project` leaves it ready, and `sync-from-template` brings it into a project that lacks it.

## Decisions

| # | Decision | Why |
|---|---|---|
| 1 | **A skill for everyday use (`issue-tracker`), a command for bulk work (`/roadmap seed`, `evaluate`, `migrate`).** | The `.claude/README.md` test: "if the user never learned this existed, should it still run?" For "note this bug" the answer is yes — a skill. Seeding and auditing the whole backlog are moments the user chooses — a command. One skill doing both would be the "skill with a mode table" that README warns against. |
| 2 | **Capture shows a draft; a plain "yes" files it.** Bulk `/roadmap` writes keep exact gate phrases. | An issue notifies people, so it is previewed. An exact phrase is friction for a one-line aside, while a batch of issues deserves the deliberate gate. |
| 3 | **Status lives in `status:*` labels**, not a Projects board's Status field. A board is an optional view. | Labels show in the issue list, and Claude and the scripts can read and set them with `gh` or the GitHub connector. A board's columns come from its own field; reading or setting it needs a token with the `project` scope, and two sources of status drift. |
| 4 | **No `status:completed`.** Closing is done; the close reason separates completed from not planned. | A label on top of the closed state can disagree with it. |
| 5 | **Labels are declared in `.github/labels.yml`, applied by `scripts/sync_labels.sh`, run by `label-sync.yml` on every push to `main`** (no path filter), plus `workflow_dispatch`. | A repo created from the template never edits `labels.yml`, so a path filter would mean it never gets labels. The dispatch trigger is how a cloud session creates them: the GitHub connector has no create-label tool, but it can run a workflow. |
| 6 | **Issue forms per type** apply `type:*` and `status:backlog`; the skill writes the same `###` sections. `check_issues.sh` reads them. | The forms make a person give context; the shared sections let one script check issues from either source. |

Supporting choices:

- **Bash 3.2.** `sync_labels.sh` and `check_issues.sh` avoid associative arrays and `${var,,}`, as the repo's other scripts do, because macOS ships bash 3.2.
- **Every `gh` call is `gh api` against REST, and repo-scoped.** In a Claude Code cloud session, `gh issue …`, `gh label …` and `gh repo view` fail with HTTP 403 because they use GraphQL, and the search API is refused because it is not scoped to the repo; `gh api 'repos/{owner}/{repo}/…'` works there, locally and in Actions. Found by running the scripts in such a session. The REST issues endpoint returns pull requests too, so `check_issues.sh` skips anything with a `pull_request` field.
- **`check_issues.sh` reads only fields `gh` and the REST API share** (`number`, `title`, `state`, `body`, label names), so it works on `gh issue list --json` output and on the connector's `list_issues` output alike.
- **Blocking writes the reason into the body's `### Dependencies`,** not only a comment, so `check_issues.sh` can tell a blocked issue with a reason from one without.
- **`check_scaffolded_project.sh` requires the issue files,** so the template's scaffold smoke test proves in CI that `init-project` keeps them.

## Ruled out

- **GitHub's native Issue Types.** Only organizations have them; labels work in every repo this template might become.
- **Automating a Projects board.** Needs a `project`-scoped token the template cannot assume; `docs/SOPs/SOP-issue-tracking.md` describes the manual setup instead.
- **Deleting labels the file does not list.** A sync that deletes would remove labels someone added by hand. GitHub's `bug` and `enhancement` duplicate `type:bug` and `type:feature`; the SOP says to delete them by hand.
- **A SessionStart hook warning when `gh` is not logged in.** The skill says so the first time it is needed, which is enough; hooks carry a high bar here.

## What this changes elsewhere

`docs/template/blueprint-review.md` rejected D2, X3 and X17 partly because this repo had "no issue policy". It has one now. Those items are not revisited here; their other reasons (GitLab-bound tooling, no recorded need) may still hold.

## What remains unverified

- The forms render, and the label workflow runs, only once they are on the default branch.
- The skill's three evaluations need a model and a GitHub repo you can write to; see `.claude/skills/README.md`.
