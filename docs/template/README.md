# Template records

This folder holds records about the template itself: the session snapshots written while working on it, and reviews or plans about how it should change. None of it belongs to a project built from the template, so `init-project` deletes the whole folder when it scaffolds one, and points `SNAPSHOT_PATH` back at `docs/session-history/`.

This repo's `SNAPSHOT_PATH` (in `CLAUDE.md`'s `## Session Config`) points here, so `/session-start` and `/session-end` read and write the template's own history in this folder.

## What belongs here

- Session snapshots from working on the template
- Reviews, comparisons and plans about the template itself, such as an assessment of another project's tooling
- Anything else that is about the template and would mislead a project that inherited it

## What does not belong here

- A project's own session snapshots (those go in docs/session-history/)
- Anything a project built from the template should keep: specs, SOPs, ADRs, plans for the project's own work (those go in their usual docs/ folders)

## Naming convention

Session snapshots: `SESSION_SNAPSHOT_YYYY-MM-DD.md`, the same as in `docs/session-history/`. Everything else: a descriptive name, with a date where it helps.

## Why a folder

`scripts/check_scaffolded_project.sh` reports this folder's existence in a scaffolded project as `TEMPLATE_RESIDUE`. It checks for the folder rather than for file names because the template adds a snapshot every session, so no list of names could stay current. `scripts/check_inherited_docs.sh` skips the folder's contents, since they are meant to talk about the template.
