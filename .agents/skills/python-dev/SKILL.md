---
name: python-dev
description: Python development best practices for Cytognosis projects
---

# Python Development Skill

You are working on a Python project within the Cytognosis ecosystem. Follow these conventions:

## Code Style
- Use **Ruff** for linting and formatting (configured in `.ruff.toml`)
- Follow **PEP 8** with a line length of 88 characters
- Use **type hints** for all function signatures
- Use **docstrings** in Google style format

## Project Structure
- Source code lives in `src/cyto_assist/`
- Tests live in `tests/`
- Use `pyproject.toml` for project configuration
- Use `uv` as the package manager

## Import Conventions
- Use absolute imports from the package root
- Group imports: stdlib → third-party → local
- Let Ruff handle import sorting via `isort` rules

## Error Handling
- Use specific exception types, never bare `except:`
- Log errors with the `logging` module
- Raise `ValueError` for invalid arguments, `TypeError` for type mismatches

## Testing
- Write tests with `pytest`
- Use fixtures from `conftest.py`
- Aim for meaningful test coverage, not 100%
- Name tests descriptively: `test_function_does_expected_behavior`
