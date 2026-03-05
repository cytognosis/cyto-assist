---
description: Run the project test suite
---

# Test Command

// turbo-all

1. Run all tests with verbose output:
```bash
uv run pytest tests/ -v --tb=short
```

2. If tests fail, check for import errors first:
```bash
uv run pytest tests/test_basic.py -v
```

3. For coverage report:
```bash
uv run pytest tests/ --cov=src/ --cov-report=term-missing
```
