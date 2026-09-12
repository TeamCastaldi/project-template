# Homelab service upgrade profiles

A cache of what has already been confirmed about specific services' upgrade
behavior, so a repeat question about the same service does not start from
zero. This is not a substitute for Step 1's documentation pull.

## Contents

- [How to use this file](#how-to-use-this-file)
- [Service upgrade profiles](#service-upgrade-profiles)
- [General upgrade-risk patterns](#general-upgrade-risk-patterns)
- [Authentik outposts](#authentik-outposts)

## How to use this file

> [!IMPORTANT]
> A row here is a starting hypothesis, not a verified answer. Never quote
> this table to Nathan as the reason an upgrade is safe — quote what
> `get_service_documentation` returned for the actual version in play. Rows
> get added at the end of a session, per the main skill's wrap-up, only
> once Nathan confirms.

## Service upgrade profiles

| Service | Category | Notes | Last confirmed |
|---|---|---|---|
| _(none profiled yet — populate after the first real upgrade check)_ | | | |

Category values:

- `Major-jump-safe` — the vendor documents that skipping major versions is
  supported
- `Sequential-step-required` — the vendor requires passing through specific
  intermediate major or minor versions in order
- `DB-migration-sensitive` — the upgrade includes a schema or data
  migration that needs a backup step, a manual trigger, or is not easily
  reversible
- `Unconfirmed` — noted as a concern but not yet checked against live
  docs; treat any claim about it as a guess until Step 1 runs

## General upgrade-risk patterns

These are categories of behavior worth watching for, not claims about any
specific service or version currently pinned in this homelab.

- Database engines with major-version bumps (Postgres, MySQL/MariaDB, and
  similar) commonly require an explicit upgrade utility or a dump/restore
  cycle rather than a plain image-tag change — confirm the exact mechanism
  for the pinned version before assuming a plain restart is enough
- Identity/SSO platforms often chain internal schema migrations across
  minor versions, which is why skipping several minor versions at once is
  a common source of failed migrations — confirm the supported jump
  distance for the version actually pinned, since it can differ release to
  release
- Reverse proxies and other largely stateless services are the more common
  "safe to jump straight to latest" category, but breaking config or label
  syntax changes between major versions (Traefik v2 to v3 labels, for
  example) still need a documentation check
- Anything that migrates persisted data in place is worth a backup step
  regardless of category — a failed migration is harder to roll back than
  the upgrade itself

> [!WARNING]
> Do not present any of the above as a fact about a specific service in
> Nathan's homelab. Step 1 must confirm behavior against that service's own
> pinned-version documentation before this section is treated as an answer
> rather than a pattern to check for.

## Authentik outposts

As of 2026-09-12 (per Nathan): four outposts exist and must move in
lockstep with the Authentik server version. This count is expected to
drift — reconfirm via `authentik_list_outposts` at the start of every
Authentik upgrade rather than trusting this number.
