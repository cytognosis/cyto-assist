# Windsurf AI Rules — Cytognosis Project

You are assisting development on a Cytognosis project: **cyto-assist**.

## Project Structure
- Source: `src/cyto_assist/`
- Tests: `tests/`
- Config: `pyproject.toml`, `.ruff.toml`, `.mypy.ini`
- Environments: managed via `scripts/setup_env.py` and Cytoskeleton

## Coding Standards
- Python 3.10+, type hints required
- Ruff for linting/formatting (line length: 88)
- Google-style docstrings
- Conventional commits (`feat:`, `fix:`, `docs:`, etc.)

## Testing
- pytest with fixtures in `conftest.py`
- Run via `uv run pytest tests/` or `nox -s test`

## Healthcare Context
- Never expose PHI in logs or outputs
- Validate all clinical data inputs
- Document model assumptions and limitations
