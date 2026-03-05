---
description: Set up the development environment
---

# Setup Command

// turbo-all

1. Create and activate the virtual environment:
```bash
python scripts/setup_env.py
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Verify the installation:
```bash
uv run pytest tests/test_basic.py -v
```

4. Check compute backend (if applicable):
```bash
uv run pytest tests/test_backend.py -v
```
