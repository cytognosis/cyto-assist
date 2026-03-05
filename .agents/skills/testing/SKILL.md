---
name: testing
description: Testing standards and pytest workflow for Cytognosis projects
---

# Testing Skill

## Framework
- Use **pytest** as the testing framework
- Configuration is in `.pytest.ini`
- Run tests via `nox -s test` or `uv run pytest tests/`

## Test Organization
```
tests/
├── conftest.py          # Shared fixtures
├── test_basic.py        # Package import and version tests
├── test_backend.py      # Compute backend verification
└── test_<module>.py     # Module-specific tests
```

## Writing Tests
- Use descriptive names: `test_<function>_<scenario>_<expected>`
- Use `pytest.fixture` for reusable test data
- Use `pytest.mark.parametrize` for data-driven tests
- Use `pytest.mark.slow` for long-running tests
- Use `pytest.mark.skipif` for conditional tests

## Running Tests
```bash
# All tests
uv run pytest tests/

# Specific file
uv run pytest tests/test_basic.py

# With coverage
uv run pytest tests/ --cov=src/ --cov-report=html

# Via nox
nox -s test
```

## Fixtures
- Define shared fixtures in `tests/conftest.py`
- Use `tmp_path` for temporary file operations
- Use `monkeypatch` for mocking environment variables
