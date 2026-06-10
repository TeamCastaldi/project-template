# db/seeds

Seed data scripts for development and testing. Not for production use.

## Rules

- Seeds must be idempotent — safe to run more than once without creating duplicate data
- Never use seeds to load production data — use proper backup/restore procedures for that
- Name files to indicate their purpose and order if sequence matters: `01_users.py`, `02_roles.py`

## Usage

```bash
# Example — run a seed script directly
python db/seeds/01_users.py

# Or via a script in scripts/ that chains them
python scripts/seed-dev-db.py
```
