# Backend

FastAPI application. All server-side application code lives here.

## Structure

```
backend/
    main.py           # FastAPI app entry point
    routers/          # Route handlers grouped by resource
    models/           # SQLAlchemy ORM models
    schemas/          # Pydantic request/response schemas
    services/         # Business logic layer
    dependencies/     # FastAPI dependency injection
    utils/            # Shared utilities (logging, config, etc.)
    requirements.txt  # Python dependencies
```

## Running locally

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

API docs available at `http://localhost:8000/docs` when running.
