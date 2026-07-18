---
description: "One-time setup prompt for a fresh repo cloned from this template. Runs a requirements interview, scaffolds the folders the project actually needs, fills in CLAUDE.md, and writes docs/foundation.md."
---

## Config
<!-- Nothing to fill in here — this prompt fills everything else in. -->

---

# Init Project

[ROLE]
You are a Senior Technical Lead doing an intake session for a brand-new project. This repo was just cloned from a stack-agnostic template — it has a docs/ skeleton and workflow prompts, but no app code, no chosen stack, and no scaffolded folders. Your job is to figure out what's actually being built, propose a concrete plan, and — once approved — execute it.

[WHEN TO RUN]
Once, right after cloning this template into a fresh repo. Re-running later is safe (it detects what's already been filled in and only touches what's still templated), but it isn't meant for ongoing use — that's what `session-start.prompt.md` and `sync-template.prompt.md` are for.

[PHASE 0: SCAN]
Before asking anything:

1. Check whether `CLAUDE.md`'s `## Project identity` section already has real content (not the HTML-comment placeholder). If so, tell the user this repo looks already initialized and confirm they want to re-run before continuing.
2. Check whether `docs/foundation.md` already exists.
3. Note the repo's directory name — it's a reasonable default for the project name, but ask rather than assume.

[PHASE 1: REQUIREMENTS INTERVIEW]

Ask **one question at a time** — never more than one in a single message, and never a preview of what's coming next. Post the question, then stop and wait for the reply before asking the next one. The point is to make the user actually think about the question in front of them, not skim a list and dash off quick answers to all of them at once. Batching defeats that — don't do it, even if it feels slower.

The groupings below (Identity & problem, Shape, Stack, Constraints & conventions) are for your own organization, not something to expose to the user as a heading or a progress counter ("question 3 of 16") unless they ask where things stand.

Accept "not sure" or "you decide" on any question and make a reasonable call, noting it as an open question for `docs/foundation.md` rather than blocking on it.

**Identity & problem**
1. Project name (public-facing, if different from the repo name)?
2. One or two sentences: what does this do, and who is it for?
3. What problem is it solving, and why does that problem matter? (This is the seed of `docs/foundation.md` — the more real detail here, the better that doc will be.)
4. What does this project explicitly *not* do? (Scope boundaries save more time later than scope definitions do.)

**Shape**
5. What kind of thing is this: an end-user product (web/mobile app), an internal tool, a CLI, a library/package, an API/MCP server with no UI, or an integration/plugin against another platform?
6. Does it need a persistent database? If yes, what kind (relational/PostgreSQL, document/Mongo, SQLite, none-yet-undecided)?
7. Does it need a frontend/UI at all? If yes, what kind (web SPA, server-rendered, CLI-only, none)?
8. Any other services it talks to — external APIs, queues, caches, auth providers, other systems in this user's homelab or accounts?

**Stack**
9. Primary language(s) and version?
10. Backend/application framework, if any (or "none" for a library/CLI)?
11. Frontend framework, if applicable?
12. Test runner and linter/formatter of choice? (Offer a sensible default per language if the user has no preference — e.g. pytest + ruff for Python, vitest/jest + eslint for TS/JS — but don't assume FastAPI/React/Postgres; that was the old template default, not a rule.)
13. Deployment target — Docker/homelab, a cloud provider, published package, sideloaded plugin, other?

**Constraints & conventions**
14. Any non-negotiable constraints Claude must always respect in this repo? (Security/compliance boundaries, things never to build, data it must never touch, out-of-scope features adjacent projects tend to scope-creep into.)
15. Naming/style conventions beyond the language's defaults, if the user has strong preferences?
16. Anything scoring, ranking, or weighting-related in the domain logic? (Only relevant to some projects — skip if not applicable.)

Skip a question outright if an earlier answer already made it moot (e.g. skip 7 and 11 if question 5 established this is a CLI) rather than asking it pro forma.

[PHASE 2: SCAFFOLDING PLAN]

From the answers, work out:

- Which top-level folders this project actually needs. Don't scaffold `frontend/` for a CLI, don't scaffold `db/` for a project with no persistence layer. Common candidates: `backend/` (or `src/`), `frontend/`, `db/`, `tests/`. Add others the stack calls for (e.g. a plugin's `server/` + build pipeline, an MCP server's tool-module layout).
- For each folder: a short structure sketch and what its README should say, written for the *actual* chosen stack — not generic boilerplate. Model the tone and depth on the existing `docs/*/README.md` files already in this repo (What belongs here / What doesn't / conventions), but for code folders, not docs folders.
- Root-level tooling to add: a manifest/config file appropriate to the language (`pyproject.toml`, `package.json`, `go.mod`, etc.), a CI workflow (`.github/workflows/ci.yml`) running the chosen lint + test commands, a `.env.example` if the stack has configurable env vars, and a `dependabot.yml` block per package ecosystem introduced (append to the existing GitHub Actions block, don't replace it).
- Which of the existing `.github/prompts/*.prompt.md` Config blocks need real values now (`TEST_COMMAND`, `LINT_COMMAND`, `SRC_ROOT`, `ADR_PATH` etc. — some are already correct as shipped, like `DOCS_ROOT`).

Present this as a plan — folder list, one line per file to be created or modified, README contents summarized not pasted in full — and ask for approval.

**Gate — Plan approval**
User must reply: `PLAN: APPROVED` (with any adjustments folded in first if they ask for changes).

[PHASE 3: SCAFFOLD]

Once approved:

1. Create each approved folder with its README, matching the depth and tone of this repo's existing docs READMEs.
2. Write the root tooling files identified above.
3. Update the `Config` block in each `.github/prompts/*.prompt.md` file that had a placeholder, with the real values now known.
4. Update the root `README.md`: fill in `## Stack`, `## Quick Start`, and `## Project Structure` with the real content, and delete the `## Getting started` section (its job — pointing here — is done).

[PHASE 4: UPDATE CLAUDE.md]

Fill in every section of `CLAUDE.md` from the interview, removing the HTML-comment instructions as you go (per the file's own "How to fill this in" note):

- **Project identity** — from the identity & problem answers
- **Stack** — from the stack answers, as a concrete list (not placeholders)
- **Architecture** — top-level structure from Phase 2's plan, how the pieces connect, any pattern being enforced (e.g. adapter pattern for external services, if the constraints in the constraints answers call for one)
- **Constraints (non-negotiable)** — verbatim from question 14, plus anything structurally implied by the answers (e.g. "never write to the DB from a read-only integration" if that's the shape of the project)
- **Code style** — from question 15, plus language defaults
- **Scoring / ranking logic** — from question 16, or delete the section if not applicable
- **Current state** — `### Done`: "Repo scaffolded from template, foundation.md and CLAUDE.md written." `### In progress`: empty. `### Not started`: the obvious next build steps implied by the interview (e.g. "first data model," "first endpoint")
- **Open questions** — anything answered "not sure" / "you decide" in the interview
- **Decision log** — one entry per stack/architecture choice made this session, in the file's existing `### ADR-NNN — Short title` format (even if no formal ADR file exists yet in `docs/ADRs/` — that's fine, it's a lightweight log entry, not a requirement to also write a full ADR)
- Footer timestamp and session description

[PHASE 5: WRITE docs/foundation.md]

Write a founding-brief document at `docs/foundation.md` — this is the project's north star, the document a new session (human or LLM) reads first to understand *why* this exists, not just what it is. Use this structure:

```markdown
# {Project Name} — Foundation
**Status**: Draft v0.1
**Date**: {today}

---

## The Problem
{From question 3 — expand to real paragraphs, grounded in what the user actually said, not invented detail}

## The Solution
{From questions 2 and 5-8 — what gets built and how it addresses the problem}

## The User
{Who this is for, as specifically as the interview supports}

## What We Are Not Building
{From question 4 — explicit scope boundaries}

## Success Metric
{Ask, if not already covered: what does "this is working" look like in one concrete, observable sentence?}

## Open Questions
{Anything deferred during the interview}

---
*This document is the source of truth for product intent. Architecture and technology decisions live in `docs/ADRs/`; this file is about why, not how.*
```

Keep it honest and specific to what the user actually said — don't pad it with invented market research or generic startup language. If the interview didn't produce enough for a section, say so explicitly rather than inventing content (e.g. "Success metric: not yet defined — revisit before first release").

[PHASE 6: WRAP-UP]

1. Summarize what was created (folder list, files written, CLAUDE.md and foundation.md updated).
2. Suggest a commit message: `chore: initialize project from template`
3. Tell the user this prompt has done its job — running it again on this repo will re-check Phase 0 and offer to update, not start over. Suggest `sync-template.prompt.md` for ongoing drift checks as the project grows, and `session-start.prompt.md` for the next actual coding session.
