# Architecture Decision Records (ADRs)

This folder contains Architecture Decision Records for the project. Each ADR documents a significant technical or structural decision — what was decided, why, what was ruled out, and what the consequences are.

ADRs are written when a decision is made and updated if circumstances change. They are not deleted — superseded decisions are marked as such and kept for historical context.

## What belongs here

- Technology choices (language, framework, database, external APIs)
- Structural patterns (adapter pattern, repository pattern, module boundaries)
- Constraint decisions (no scraping, BYOK model, CLI-only scope)
- Anything where future-you (or a new collaborator) would ask "why did we do it this way?"

## What does not belong here

- Implementation details (those go in docs/specs/)
- Project timelines or milestones (those go in docs/plans/)
- Runbooks or procedures (those go in docs/SOPs/)

## Naming convention

`ADR-NNN-short-description.md` — e.g. `ADR-001-database-choice.md`

## Status values

| Status | Meaning |
|--------|---------|
| Accepted | In effect, follow this decision |
| Draft | Under discussion, not yet binding |
| Deprecated | No longer relevant but kept for history |
| Superseded | Replaced by a later ADR — link provided |

## Index

Every ADR file in this folder gets a row here — this table, plus `CLAUDE.md`'s `## Decision log`, is how a reader finds the right file without opening each one. Keep it in sync: add a row the moment a new ADR is written, and update the Status column the moment one changes. `CLAUDE.md` should never host a decision's actual content — only a link into this table.

| ADR | Title | Status |
|-----|-------|--------|
| _none yet_ | — | — |
