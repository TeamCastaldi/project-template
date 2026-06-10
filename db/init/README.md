# db/init

One-time database initialization scripts. These run once per environment to set up the database itself before migrations can run.

## What belongs here

- Create database and roles scripts
- PostgreSQL extension setup (e.g. `uuid-ossp`, `pgcrypto`, `pg_trgm`)
- Initial permissions and grants
- Environment-specific setup (e.g. test database creation)

## Important

These scripts are not managed by Alembic — they are prerequisites to Alembic. Run them manually when setting up a new environment, then run migrations.

```bash
# Typical setup order for a new environment
psql -U postgres -f db/init/01_create_db.sql
psql -U postgres -f db/init/02_extensions.sql
alembic upgrade head
python db/seeds/01_users.py   # development only
```

See `docs/SOPs/` for the full environment setup procedure.
