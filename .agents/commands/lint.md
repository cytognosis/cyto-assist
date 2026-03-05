---
description: Run linters and formatters
---

# Lint Command

// turbo-all

1. Run Ruff linter:
```bash
uv run ruff check src/ tests/
```

2. Run Ruff formatter:
```bash
uv run ruff format src/ tests/
```

3. Run type checker:
```bash
uv run mypy src/
```
