# SOP: Tracking work in GitHub Issues

## Purpose

Keep everything this project plans to do — features, bugs, tech debt, rough ideas — as GitHub Issues, so there is one place to look, one history per item, and one way to say "done": closing it. Labels give the list its shape; milestones and an optional Projects board give it views.

## When to use it

- You notice a bug, an idea or a missing piece while working on something else.
- You start, pause, finish or drop a piece of planned work.
- You want to see what is in flight, what is next, or what is stuck.

A small fix you are about to make anyway needs no issue — go straight to a branch.

## Prerequisites

None in a repo set up from these files: `.github/labels.yml` defines the labels, and the **Sync labels** workflow (`.github/workflows/label-sync.yml`) creates them on every push to `main`. If the labels are missing — a repo with no push to `main` yet, or Actions turned off — run the workflow from the Actions tab, or locally:

```bash
bash scripts/sync_labels.sh          # needs gh, logged in
```

For Claude to work with issues, it needs GitHub access: in a cloud session, the GitHub connector; on your own machine, `gh` installed and logged in (`gh auth login`).

## The labels

Every open issue carries one **status** and one **type**. **Priority** is set at triage, when an issue moves out of backlog, and only from what someone decided.

| Family | Label | Meaning |
|---|---|---|
| Status | `status:backlog` | Noted, not yet prioritized |
| | `status:planned` | Committed to: up next |
| | `status:in-progress` | Being worked on now |
| | `status:blocked` | Waiting on another issue or an outside party; what it waits on is under `### Dependencies` |
| Type | `type:feature` | New functionality |
| | `type:improvement` | Refines something that already works |
| | `type:bug` | Something is broken |
| | `type:debt` | Refactoring, tech debt or infrastructure |
| | `type:idea` | Low-fidelity idea, not yet shaped into work |
| Priority | `p0:critical` · `p1:high` · `p2:medium` · `p3:low` | Must have · Important · Nice to have · Backburner |

There is no "completed" status. Closing an issue is what marks it done, and the close reason says whether it was *completed* or *not planned*.

`.github/labels.yml` is the single definition. To add, rename or recolour a label, edit that file and push to `main`; the workflow applies it. It never deletes labels, so GitHub's defaults (`bug`, `enhancement`, `good first issue` and the rest) stay until you delete them in the repo's Labels page — worth doing for `bug` and `enhancement`, which duplicate `type:bug` and `type:feature`.

## Procedure

### Filing an issue

- **Talk to Claude.** "Note that export breaks on Safari, we'll fix it later." The `issue-tracker` skill drafts the issue — title, labels, the right sections, with anything you did not say marked `_Not yet known_` — and files it when you say yes.
- **Or use the web form.** New issue offers five forms: Feature, Improvement, Bug, Tech debt, Idea. Each applies its type label and `status:backlog`, and asks for the sections that type needs:
  - **Context** — why do this?
  - **User story** — "As a [user], I want to [action] so that [value]."
  - **Acceptance criteria** — a checklist of what "done" looks like.
  - **Dependencies** — issues that must be finished first, as `#N`.

  An idea asks only for the idea; when it is picked up, it is reshaped into one of the other types.

Titles start with a verb: "Implement OAuth2 login", not "Login".

### Moving work along

| To | Do |
|---|---|
| Commit to it | Swap `status:backlog` for `status:planned`, and set a priority |
| Start it | Swap to `status:in-progress`; open a branch; put `Closes #N` in the PR |
| Mark it blocked | Swap to `status:blocked`; write what it waits on under `### Dependencies` and in a comment |
| Finish it | Merge the PR that says `Closes #N` — GitHub closes the issue |
| Drop it | Close as *not planned*, with a one-line reason |

An issue has exactly one status label at a time. Tell Claude "start #12" or "#12 is blocked on the API change" and the skill makes the swap; `/session-start` offers in-progress and planned issues as the session's mission.

### Reviewing the backlog

- **"What's open?"** — ask Claude, or run the checker yourself:

  ```bash
  gh issue list --state open --limit 1000 --json number,title,state,labels,body \
    | bash scripts/check_issues.sh -
  ```

  It lists open issues in pick-up order and flags ones whose labels or sections are off.
- **`/roadmap evaluate`** — a full audit: issues that look done but are open, blocked issues whose blockers closed, drift, and goals in the project's docs with no issue.
- **`/roadmap seed`** — file issues for the goals in `docs/foundation.md`, `CLAUDE.md` and the rest, each citing where it came from.

### Milestones

Use a milestone for a time box or a release — "v1.0", "Q3". It gives a due date and a progress bar (open versus closed). Assign issues to it as they are planned; an issue in backlog usually has none.

### A board view (optional)

For a Kanban board or a timeline, create a GitHub Project (your profile or organization → Projects → New project → Board), then:

1. Workflows → **Auto-add to project**: filter `is:issue`, this repo.
2. Workflows → **Item closed**: set Status to Done.

A board's columns come from the project's own Status field, not from labels, so moving a card does not change a `status:*` label. Labels stay the source of truth here — Claude and the scripts read them — so either keep the board as a view you update alongside, or group a table view by label.

## Old way, new way

| Old way (a roadmap file) | New way (GitHub Issues) |
|---|---|
| **Adding an item:** type a line in a doc | Create an issue (or tell Claude), labelled `type:idea` or another type |
| **Prioritizing:** re-order lines in a list | Set a `p0`–`p3` label, or move cards on a board |
| **Updating progress:** edit the text | Swap the status label, or close the issue |
| **Tracking history:** read old versions of the doc | Read the issue's comments, links and closed state |

## Verification

- `bash scripts/sync_labels.sh --check` exits 0: the repo has every label in `.github/labels.yml`.
- `check_issues.sh` (above) exits 0: every open issue has one status and one type, planned work has a priority and acceptance criteria, and every blocked issue says what it waits on.
