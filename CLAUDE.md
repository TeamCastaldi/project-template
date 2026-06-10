# CLAUDE.md

This file is the primary context document for Claude (and other LLM assistants) working in this repository. Fill it in as the project takes shape. An incomplete CLAUDE.md is better than none — add sections as you know them.

---

## How to fill this in

This file should be filled in during or just after initial project setup, then kept current as the project evolves. The best time to update it is at the end of a working session, before you close the repo.

Each section below has a comment explaining what to put there. Remove the comments as you fill in real content.

A well-maintained CLAUDE.md means every new LLM session starts with full context instead of having to rediscover the project from scratch.

---

## Project identity

<!-- 
What does this project do? 2-3 sentences max.
Include the public name if different from the repo name.
Who is the intended user?
-->

## Stack

<!-- 
List the concrete technologies in use:
- Language and version (e.g. Python 3.11)
- Web framework (e.g. FastAPI)
- Frontend (e.g. React 18 / Vite)
- Database and ORM (e.g. PostgreSQL / SQLAlchemy + Alembic)
- Test runner (pytest)
- Linter/formatter (ruff)
- Any other key dependencies
-->

## Architecture

<!--
Describe the top-level structure of the codebase:
- What lives in backend/, frontend/, db/
- How the pieces connect (e.g. "FastAPI serves a REST API consumed by the React frontend")
- Any key patterns enforced (e.g. provider adapter pattern, repository pattern)
- Data flow at a high level
-->

## Constraints (non-negotiable)

<!--
Things Claude must never do in this repo.
Be explicit. Examples:
- Never commit .env or any file containing secrets
- Never add GUI to the CLI path
- Never bypass the adapter pattern for external APIs
- Never store PII in profiles
-->

## Code style

<!--
- Naming conventions (snake_case for Python, PascalCase for React components, etc.)
- Docstring format (Google style recommended)
- Type hints: required or optional?
- Error handling patterns
- Logging: how and where (e.g. always use setup_logger(__name__))
- Any patterns to avoid
-->

## Scoring / ranking logic (if applicable)

<!--
If this project scores, ranks, or weights things:
- What are the weights and what do they mean?
- Where does this logic live?
- What is and isn't handled by LLM vs deterministic code?
-->

## Current state

<!--
Keep this current. Update at the end of each session.
Format:
### Done
- bullet list of completed work

### In progress
- bullet list of active work

### Not started
- bullet list of planned but untouched work
-->

### Done

### In progress

### Not started

## Open questions

<!--
Known ambiguities, deferred decisions, or things that will 
trip up a new LLM session if not documented.
Format: numbered list, one question per item.
Remove items when resolved and add a note to the relevant ADR or spec.
-->

## Decision log

<!--
A running summary of key decisions. For full context see docs/ARDs/.
Format:
### ADR-NNN — Short title
- One line summary of the decision
- Key consequence
- What was ruled out
-->

---

*Last updated: {date} | Session: {brief description}*
