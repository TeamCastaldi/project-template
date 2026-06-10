# {PROJECT_NAME}

{One or two sentence description of what this project does and who it's for.}

---

## Stack

- **Backend**: Python / FastAPI
- **Frontend**: React / Vite
- **Database**: {e.g. PostgreSQL, MongoDB}
- **Tests**: pytest
- **Lint/Format**: ruff

## Quick Start

```bash
# 1. Clone and enter the repo
git clone {repo-url}
cd {project-name}

# 2. Copy environment template and fill in values
cp .env.example .env

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Install frontend dependencies
cd frontend && npm install

# 5. Run backend
uvicorn backend.main:app --reload

# 6. Run frontend (separate terminal)
cd frontend && npm run dev
```

## Project Structure

```
backend/        FastAPI application
frontend/       React + Vite application
db/             Migrations, seeds, schema, init scripts
docs/           All project documentation
scripts/        Dev-time utilities (not shipped)
tests/          pytest test suite
```

For architecture decisions, see `docs/ARDs/`.
For technical specs, see `docs/specs/`.
For SOPs and runbooks, see `docs/SOPs/`.
