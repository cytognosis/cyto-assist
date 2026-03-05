---
description: How to add a new feature to the project
---

# New Feature Workflow

1. Create a feature branch:
```bash
git checkout -b feat/<feature-name>
```

2. Create tests first (TDD approach):
   - Add test file in `tests/test_<feature>.py`
   - Write failing tests that define the expected behavior

3. Implement the feature:
   - Add source code in `src/cyto_assist/`
   - Follow module structure: `tl/` for tools, `pp/` for preprocessing, `pl/` for plotting

4. Run linters and formatters:
```bash
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
```

5. Run tests:
```bash
uv run pytest tests/ -v
```

6. Commit with conventional commit format:
```bash
git add .
git commit -m "feat: <description of the feature>"
```

7. Push and create PR:
```bash
git push origin feat/<feature-name>
```
