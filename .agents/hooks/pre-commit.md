---
description: Pre-commit checks for agents to follow
---

# Pre-Commit Hook

Before committing, ensure:

1. All files are formatted: `uv run ruff format --check src/ tests/`
2. No linting errors: `uv run ruff check src/ tests/`
3. Tests pass: `uv run pytest tests/ -x --tb=short`
4. No large files (>5MB) are staged
5. Commit message follows conventional format: `type(scope): description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`
