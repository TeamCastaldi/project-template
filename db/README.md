# Database

All database-related files live here, regardless of the database engine in use. This folder is engine-agnostic — PostgreSQL, MongoDB, SQLite, or others all follow the same structure.

## Structure

```
db/
    migrations/     Alembic migration files (SQL schema changes over time)
    seeds/          Seed data scripts for development and testing
    schema/         Schema definitions, ERDs, or data model documentation
    init/           Database initialization scripts (create DB, roles, extensions)
```

## migrations/

Alembic migration files. Each migration is a versioned, reversible change to the database schema. Never edit a migration that has already been applied — create a new one instead.

To create a new migration:
```bash
alembic revision --autogenerate -m "description of change"
```

To apply migrations:
```bash
alembic upgrade head
```

## seeds/

Scripts that populate the database with development or test data. Not for production use. Seeds should be idempotent — safe to run more than once.

## schema/

Human-readable schema documentation. ERDs, table descriptions, field definitions. Useful for onboarding and for LLM context. Keep in sync with the actual migrations.

## init/

One-time setup scripts — creating the database, setting up roles and permissions, enabling PostgreSQL extensions (e.g. `uuid-ossp`, `pgcrypto`). Run once per environment, not per deployment.
