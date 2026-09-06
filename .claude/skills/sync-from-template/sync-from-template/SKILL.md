---
name: sync-from-template
description: "Pulls the .claude and .github/prompts folders from Nathan's project-template repo into the current repo (a project scaffolded from that template), with a file-by-file diff and confirmation before anything is overwritten. Trigger this whenever Nathan says '/sync-from-template', asks to sync, pull, or update prompts or tooling from the template, says the template has newer prompts than this repo, asks to check this repo against project-template, or wants to catch up on template changes -- even if he does not name the skill. This is the mirror image of the template repo's own sync-template.prompt.md, which audits the template's internal consistency with itself. This skill instead reaches OUT from a downstream project repo back to the template to pull specific folders in. Do not use this for auditing a repo's own internal folder, README, or CLAUDE.md consistency -- that is a separate concern handled by sync-template.prompt.md inside the template repo itself."
---

# Sync from template

## What this does

Reaches from the current repo (a project created from `project-template`) back to
the template repo, and pulls its current `.claude` and `.github/prompts` folders
in. Every file that differs is shown as a diff and held for confirmation before
it touches anything on disk. Nothing is overwritten silently.

## When to use this

Run it when Nathan:

- Asks to sync, pull, or update prompts or tooling from the template
- Says the template has picked up new prompts, skills, or `CLAUDE.md` changes
- Wants to check whether this repo is behind `project-template`
- Types `/sync-from-template`

Do not confuse this with `sync-template.prompt.md`. That prompt lives inside the
template repo and audits the template's own internal consistency (folders vs.
READMEs, prompt configs vs. reality). This skill lives inside a *downstream*
project repo and pulls two specific folders in from the template. Different
repo, different direction, different job.

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
  - .github/prompts
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

✅ Up to date:       [files marked SAME]
🔄 Changed upstream: [files marked CHANGED]
➕ New in template:  [files marked NEW]
❓ Local-only:       [files marked LOCAL_ONLY -- never auto-removed]
```

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

### 4. Clean up

Once Nathan is done applying changes (or decides not to apply any), remove
the temp clone:

```bash
rm -rf "$TEMP_CLONE"
```

This is safe to run without asking first -- `$TEMP_CLONE` is a directory this
skill created a few minutes ago under `mktemp -d`, not anything of Nathan's.

### 5. Suggest a commit

Once at least one file was applied, suggest (don't run) a commit:

```text
chore(tooling): sync .claude/.github/prompts from project-template@<short-sha>
```

## Boundaries

- Never invent `template_repo_url` -- ask if the config file doesn't have it.
- Never overwrite a `CHANGED` or apply a `NEW` file without an explicit
  `SYNC: PULL` confirmation for it.
- Never touch a `LOCAL_ONLY` file. Ever. That's out of scope for this skill,
  not just gated behind a confirmation phrase.
- Never leave a temp clone behind after the sync is done or abandoned.
