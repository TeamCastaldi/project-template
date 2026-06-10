# Tests

pytest test suite. All automated tests live here.

## Structure

```
tests/
    conftest.py         Shared fixtures and pytest configuration
    unit/               Unit tests (single function or class in isolation)
    integration/        Integration tests (multiple components together)
    e2e/                End-to-end tests (full request/response cycles)
```

## Running tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific file
pytest tests/unit/test_auth.py

# Run tests matching a keyword
pytest -k "test_login"
```

## Conventions

- Test files are named `test_{module}.py`
- Test functions are named `test_{what_it_does}`
- Each test should test one thing
- Use fixtures in `conftest.py` for shared setup
- Tests must pass before any PR is merged — CI enforces this
