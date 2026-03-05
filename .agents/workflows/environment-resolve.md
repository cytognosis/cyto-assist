---
description: How to resolve or rebuild the project environment
---

# Environment Resolve Workflow

1. Check current environment status:
```bash
uv run python -c "import sys; print(sys.version)"
```

2. If the environment needs rebuilding, use the setup script:
```bash
python scripts/setup_env.py --strategy resolve --env-name ml --compute-backend rocm
```

3. Verify PyTorch and compute backend:
```bash
uv run pytest tests/test_backend.py -v
```

4. If using Cytoskeleton, update the submodule first:
```bash
git submodule update --remote modules/cytoskeleton
```

5. Then re-resolve:
```bash
python scripts/setup_env.py --strategy resolve --env-name ml --compute-backend rocm
```
