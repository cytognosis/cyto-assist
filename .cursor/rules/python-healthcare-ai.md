---
description: Python Healthcare AI coding standards and best practices
globs: ["**/*.py"]
---
# Python Healthcare AI Coding Standards

## Core Principles

1.  **Safety First**: Patient safety and data integrity are paramount.
2.  **Reproducibility**: All results must be reproducible.
3.  **Explainability**: AI models should be interpretable where possible.
4.  **Compliance**: Adhere to HIPAA, GDPR, and other relevant regulations.

## Development Guidelines

### Virtual Environments
- Always use the project's virtual environment (managed by `uv`).
- Do not install packages globally.

### Code Quality
- Follow PEP 8 (enforced by `ruff`).
- Use type hints for all function signatures (enforced by `mypy`).
- meaningful variable names (no single letter variables except `i`, `j`, `k` in loops).

### Libraries and Tools
- **DataFrames**: Use `pandas` (or `polars` if performance requires).
- **Arrays**: Use `numpy` or `torch.Tensor`.
- **ML Framework**: Use `pytorch` via `lightning` for structured training.
- **Plotting**: Use `matplotlib`, `seaborn`, or `plotly`.

### Healthcare Specifics
- **Data Handling**: Never hardcode PHI (Protected Health Information).
- **Logging**: Do not log sensitive patient data.
- **Validation**: Validate all medical data inputs against schema.
- **Identifiers**: Use UUIDs or internal IDs, never MRNs or SSNs in codebase.
