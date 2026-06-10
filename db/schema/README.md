# db/schema

Human-readable schema documentation — table definitions, field descriptions, relationships, and ERDs.

This folder documents what the database looks like and why. It is not executable — the source of truth for the actual schema is the migrations in `db/migrations/`.

## What belongs here

- ERDs (entity relationship diagrams) as images or Mermaid markdown
- Table-by-table field descriptions with types, constraints, and purpose
- Notes on indexing strategy and why specific indexes exist
- Documentation of any non-obvious design decisions (e.g. why a field is nullable, why a JSONB column was chosen)

## Keeping it in sync

Update this folder whenever a migration adds or changes something significant. A schema doc that drifts from the actual database is worse than no doc at all.
