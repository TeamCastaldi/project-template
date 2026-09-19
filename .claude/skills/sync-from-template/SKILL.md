---
name: sync-from-template
description: "Pulls the .claude folder (commands and skills) from Nathan's project-template repo into the current repo (a project scaffolded from that template), with a file-by-file diff and confirmation before anything is overwritten. Trigger this whenever Nathan says '/sync-from-template', asks to sync, pull, or update commands, skills, or tooling from the template, says the template has newer tooling than this repo, asks to check this repo against project-template, or wants to catch up on template changes -- even if he does not name the skill. This is the mirror image of the /sync-template command, which audits a repo's internal consistency with itself. This skill instead reaches OUT from a downstream project repo back to the template to pull specific folders in. Do not use this for auditing a repo's own internal folder, README, or CLAUDE.md consistency -- that is a separate concern handled by the /sync-template command."
---

# Sync from template

## What this does

Reaches from the current repo (a project created from `project-template`) back to
the template repo, and pulls its current `.claude` folder — commands and
skills — in. Every file that differs is shown as a diff and held for confirmation before
it touches anything on disk. Nothing is overwritten silently.

## When to use this

Run it when Nathan:

- Asks to sync, pull, or update commands, skills, or tooling from the template
- Says the template has picked up new commands, skills, or `CLAUDE.md` changes
- Wants to check whether this repo is behind `project-template`
- Types `/sync-from-template`

Do not confuse this with the `/sync-template` command. That command audits a
repo's own internal consistency — folders vs. READMEs, documented commands vs.
reality — without reaching outside it. This skill reaches from a *downstream*
project repo back to the template and pulls a folder in. Different direction,
different job.

## One-time setup: the config file

The first time this runs in a repo, look for `.claude/sync-from-template.yaml`.
If it does not exist, this is a first run: propose the defaults below (this is
Nathan's one template repo, so the URL and branch are already known), let him
confirm or override, and create the file.

```yaml
# .claude/sync-from-template.yaml
# Fill in once, when this repo is set up. Committed to the repo so it travels
# with clones and doesn't live only in one machine's git config.
template_repo_url: https://github.com/TeamCastaldi/project-template.git
template_ref: main
sync_paths:
  - .claude
```

> [!NOTE]
> This repo does not currently record its template origin anywhere else (e.g.
> in `CLAUDE.md`). If `init-project` starts doing that later, read that value
> first and treat this file as the fallback -- don't ask Nathan to duplicate
> the same URL in two places once there's a single source of truth for it.

Proposing the default above on first run is fine -- it's a known, confirmed
value, not a guess. If Nathan ever points this skill at a different template
repo, or the default above stops being accurate, don't invent a replacement
URL; stop and ask.

## Workflow

### 1. Fetch and compare

Run [`scripts/compare_template.sh`](scripts/compare_template.sh) with the
values from the config file:

```bash
scripts/compare_template.sh "$TEMPLATE_REPO_URL" "$TEMPLATE_REF" "$PROJECT_ROOT" "${SYNC_PATHS[@]}"
```

This does an ephemeral sparse clone of the template (shallow, blob-filtered,
scoped to `sync_paths` only) into a temp directory, then reports how every
file under those paths compares to the local repo. It never touches the local
repo itself -- it only reads and reports. Read
[`scripts/compare_template.sh`](scripts/compare_template.sh) itself if you
need to understand exactly what it does before running it; it is short and
worth reading rather than trusting blindly.

The script's output gives you four buckets per file: `NEW`, `CHANGED`, `SAME`,
`LOCAL_ONLY`. It also prints `TEMP_CLONE=<path>` (where the fetched template
copy lives) and `TEMPLATE_SHA=<short sha>` (the commit you're comparing
against). Keep both of these -- you need them for the rest of the workflow.

It also prints `TEMPLATE_VERSION` and `PROJECT_VERSION`, read from each side's
`.template-version`. These turn the report from a raw file diff into a
statement of how far behind this project is:

- **Both known and different** -- name the gap (`1.4.0 -> 2.1.0`) and read
  `CHANGELOG.md` from `$TEMP_CLONE` for the entries between them. A **Major**
  entry means a downstream project is expected to act by hand, so surface those
  before showing any file diffs: they explain *why* files changed, which is the
  thing a file-by-file diff cannot tell anyone.
- **Both known and equal** -- say so. Any `CHANGED` file is then a local edit,
  not an upstream update, and that is worth pointing out rather than offering to
  overwrite.
- **`PROJECT_VERSION=unknown`** -- this project predates template versioning.
  Offer to write the current `TEMPLATE_VERSION` into `.template-version` as part
  of this sync, so the next run can report a real gap.
- **`TEMPLATE_VERSION=unknown`** -- the pinned ref predates versioning. Fall back
  to the SHA and say that is what you are comparing against.

We use an ephemeral clone rather than a persistent `template` git remote on
purpose: the only thing that needs to know where the template lives is the
config file above. If the template ever moves, Nathan changes one YAML value
and every future sync just picks it up, instead of having to also update a
remote URL that isn't tracked anywhere. This does mean a fresh clone on every
run instead of an incremental fetch -- if that ever becomes slow enough to be
annoying, a persistent remote is the fallback; revisit then.

### 2. Report

Present the comparison grouped by status, in this format:

```text
TEMPLATE SYNC REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Comparing against project-template @ <template_ref> (commit <sha>)
Version: <PROJECT_VERSION> -> <TEMPLATE_VERSION>

⚠️  Needs manual action: [Major changelog entries between the two versions]
✅ Up to date:       [files marked SAME]
🔄 Changed upstream: [files marked CHANGED]
➕ New in template:  [files marked NEW]
❓ Local-only:       [files marked LOCAL_ONLY -- never auto-removed]
```

Drop the version line if both sides are `unknown`, and drop the manual-action
row when there are no Major entries between the two versions -- an empty row
reads as a warning that never resolves.

If every file is `SAME`, say so plainly and stop -- there's nothing to
confirm or apply.

### 3. Confirm and apply, one file at a time

For each `CHANGED` file, show a real diff before asking for anything:

```bash
diff -u "$PROJECT_ROOT/$rel" "$TEMP_CLONE/$rel"
```

For each `NEW` file, show its content (it's new, there's nothing to diff
against).

Wait for one of these before touching disk:

- `SYNC: PULL <path>` -- apply that one file
- `SYNC: PULL ALL` -- apply every `CHANGED` and `NEW` file reported

To apply a file, copy it from the temp clone over the local path, creating
parent directories if the file is new:

```bash
mkdir -p "$(dirname "$PROJECT_ROOT/$rel")"
cp "$TEMP_CLONE/$rel" "$PROJECT_ROOT/$rel"
```

`LOCAL_ONLY` files are report-only. Never delete, move, or modify them,
regardless of what confirmation phrase Nathan gives -- there is no phrase
that authorizes touching them. If a file only exists locally, that's either
intentional local customization or something the template dropped; either
way it needs a human to look at it deliberately, not this skill deciding on
its behalf.

### 4. Stamp the version

Once at least one file has been applied, write the template version this sync
brought the project up to:

```bash
echo "$TEMPLATE_VERSION" > "$PROJECT_ROOT/.template-version"
```

Do this only when files were actually applied, and only when
`TEMPLATE_VERSION` is not `unknown`. A project that declined every change is
still on its old version, and a marker claiming otherwise makes the next sync
report a gap that does not exist -- worse than having no marker at all.

If Nathan applied only some of the `CHANGED` files, say so and ask before
stamping: the version is a claim about the whole synced tree, and a partial
apply does not support it.

### 5. Clean up

Once Nathan is done applying changes (or decides not to apply any), remove
the temp clone:

```bash
rm -rf "$TEMP_CLONE"
```

This is safe to run without asking first -- `$TEMP_CLONE` is a directory this
skill created a few minutes ago under `mktemp -d`, not anything of Nathan's.

### 6. Suggest a commit

Once at least one file was applied, suggest (don't run) a commit:

```text
chore(tooling): sync .claude from project-template@<short-sha>
```

When a version was stamped, name it instead -- it means more to a reader six
months out than a short SHA does:

```text
chore(tooling): sync tooling from project-template 1.4.0 -> 2.1.0
```

## Boundaries

- Never invent `template_repo_url` -- ask if the config file doesn't have it.
- Never overwrite a `CHANGED` or apply a `NEW` file without an explicit
  `SYNC: PULL` confirmation for it.
- Never touch a `LOCAL_ONLY` file. Ever. That's out of scope for this skill,
  not just gated behind a confirmation phrase.
- Never leave a temp clone behind after the sync is done or abandoned.
