# Scripts

Dev-time utilities that support development but are not part of the shipped product. Scripts here are tools for the developer, not the application.

## What belongs here

- Environment setup helpers
- Data import/export utilities
- Local development conveniences (reset DB, generate test data, etc.)
- Build or deployment helpers that don't belong in CI
- One-off migration or cleanup scripts (keep even after use — they document what was done)

## What does not belong here

- Application code (that goes in backend/)
- Test files (those go in tests/)
- CI/CD pipeline definitions (those go in .github/workflows/)

## Conventions

- Name scripts clearly: `reset-db.py`, `seed-dev-data.sh`, `export-users.ps1`
- Include a docstring or comment block at the top of each script explaining what it does, when to use it, and any required environment variables
- Cross-platform where possible — if a script is Windows-only or Linux-only, say so at the top
- Never hardcode secrets — read from environment variables or .env
