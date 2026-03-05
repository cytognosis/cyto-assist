---
description: Documentation standards for Python code
globs: ["**/*.py", "**/*.md"]
---
# Documentation Standards

## Docstrings
- Format: **Google Style**.
- Mandatory for: Public modules, classes, methods, functions.
- content:
    - **Args**: Name, type, description.
    - **Returns**: Type, description.
    - **Raises**: Error type, condition.

## Tutorials
- Use Jupyter Notebooks or `myst-nb` markdown.
- Explain "Why" and "How", not just "What".
- Include visualizations where applicable.

## API Docs
- Generated via Sphinx.
- Ensure type hints are correct for `autodoc`.
