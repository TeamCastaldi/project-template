---
name: version-upgrade-planner
description: >
  Pre-emptive risk assessment for bumping a pinned service version in the
  Team Castaldi homelab — used before anything breaks, not after. Always
  pulls official version-specific documentation before advising, classifies
  each upgrade as a safe direct jump, a required staged/sequential path, or
  a database-migration-sensitive change, and works on exactly one service
  at a time (Authentik plus its outposts counts as one). Use this whenever
  Nathan asks whether it is safe to bump a homelab service's pinned
  version, wants to check for pending image updates or CVEs across the
  fleet, asks about the upgrade path between two versions, or wants to plan
  a version bump before touching a compose file. This is the proactive
  counterpart to the troubleshooting skill — if a bump already broke
  something, troubleshooting handles it, not this skill.
---

# Version upgrade planner

Decide whether, and how, to move a pinned service version forward — before
anything is broken. This is planning work, not incident response: the
question in play is "is this safe and what is the right path," not "what
just broke."

## Relationship to other skills

- **troubleshooting** owns the reactive case: something already broke,
  possibly because of a past bump, or a bump is the theorized fix for an
  existing symptom. If a bump made during Step 3 here fails verification,
  stop and hand off to troubleshooting rather than re-diagnosing inside
  this skill.
- **dependabot-pr-consolidator** currently owns the code-repository side of
  this same concern — SemVer risk tiers, and cross-checking a bump against
  other pinned versions in a repo. This skill reuses that vocabulary for
  homelab pinned image versions. Whether dependabot-pr-consolidator should
  fold into this skill as a `references/code-repo.md` file — the same move
  troubleshooting made when it replaced three older skills — is still an
  open question. Flag it to Nathan rather than assuming either way.

## Why this is gated

Two failure modes this guards against: assessing an upgrade from memory
instead of the documented behavior for that specific version, and touching
more than one service at a time in an environment where a bad upgrade
cascades past the service itself (Traefik, Authentik, and NFS failures all
do — see troubleshooting's incident severity table).

Do not proceed past a gate on implied approval. "Sounds right," "yeah," or
silence are not the confirmation phrase. Ask again rather than assuming.

## Step 0 — Identify the service

> [!IMPORTANT]
> **Single-service rule.** Work on exactly one service per session. If the
> prompt does not name exactly one service, the first thing back to Nathan
> is a question capturing which one — not a plan, not a documentation pull,
> nothing else. Offering to run a fleet-wide scan
> (`dockhand_list_pending_updates`, `dockhand_list_vulnerabilities`) to help
> him choose is fine as part of that same question — but a choice is still
> required before Step 1 starts.
>
> **The one exception:** Authentik. The server and its outposts move
> together as a single upgrade — treat "Authentik" as the service, not each
> outpost individually. Do not trust a remembered outpost count (four, as
> of this writing) — call `authentik_list_outposts` at the start of every
> Authentik upgrade to confirm which outposts actually exist, since this
> list is expected to change over time.

## Step 1 — Pull documentation, then classify

> [!WARNING]
> Never assess upgrade safety from memory or general knowledge of "how this
> kind of software usually behaves." Call `get_service_documentation` for
> both the current pinned version — read it from the compose file's
> `${_VERSION}` variable or `registry_get_service`, never assumed — and the
> target version, before saying anything about risk, path, or migrations.
> Every time, no exceptions. If documentation-mcp errors out or has no
> source for either version, say so plainly and treat the assessment as
> unconfirmed rather than filling the gap from training data.

With docs in hand, work out:

1. **SemVer risk tier** — patch, minor, or major, per the target version's
   own versioning promise (same vocabulary as dependabot-pr-consolidator
   uses for code dependencies)
1. **Upgrade path shape** — one of:
   - **Direct-safe** — the docs state that skipping straight to the target
     is supported
   - **Sequential-step-required** — the docs require passing through named
     intermediate versions in order; list them explicitly
   - **DB-migration-sensitive** — the upgrade includes a schema or data
     migration; note whether it runs automatically on container start,
     needs a manual command, and whether it is reversible
1. Check `references/homelab-services.md` for a prior profile on this
   service. Treat any match as a hypothesis to confirm against what was
   just pulled, not a substitute for pulling it — a profile can go stale.

## Step 2 — Present the plan

Present:

- **Current → target version**, and the risk tier
- **Path** — direct, or the exact sequence of intermediate versions
- **What the docs actually say** — the specific breaking changes or
  migration notes behind the classification, not a paraphrase of "it
  should be fine"
- **Backup step**, if the upgrade touches persisted data
- **Rollback plan** — pin back to the current version in compose
- For Authentik specifically: every outpost affected and its current
  version, from `authentik_list_outposts` / `authentik_get_outpost_status`
  — not from memory

> [!IMPORTANT]
> **Gate — plan approval.** Nathan replies `PLAN: APPROVED`. Anything
> else — a question, a change to the target version, silence — is not
> approval. Revise and re-present.

## Step 3 — Execute and verify

```bash
docker compose -f ~/homelab/nodes/<node>/<service>/compose.yaml pull
docker compose -f ~/homelab/nodes/<node>/<service>/compose.yaml up -d --force-recreate
docker compose -f ~/homelab/nodes/<node>/<service>/compose.yaml logs --tail=100 --no-color
docker compose -f ~/homelab/nodes/<node>/<service>/compose.yaml ps
```

For a DB-migration-sensitive upgrade, confirm the migration actually
completed by reading the logs, not just the container status — "running"
only means the process started, not that the migration finished.

Rollback, if needed:

```bash
git checkout ~/homelab/nodes/<node>/<service>/compose.yaml
docker compose -f ~/homelab/nodes/<node>/<service>/compose.yaml up -d
```

> [!IMPORTANT]
> **Gate — result.** Nathan replies `VERIFIED` or `FAILED: <symptom>`.
>
> On `FAILED`, stop. This is now a troubleshooting case — hand off rather
> than continuing to iterate inside this skill.

## Wrap-up

Once the result gate clears with `VERIFIED`:

- Propose an update to `references/homelab-services.md` for this
  service — category, what the docs said, today's date — and write it only
  with Nathan's confirmation
- Note anything discovered that should also update troubleshooting's
  homelab reference (a new safety-rule case, a routing gotcha hit during
  the restart). That file belongs to a different skill — name the specific
  line for him rather than editing it from here
