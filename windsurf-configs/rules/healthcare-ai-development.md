---
description: Comprehensive healthcare AI development guidelines
globs: ["**/*.py", "**/*.ipynb"]
---
# Healthcare AI Development Guidelines

## 1. Compliance & Safety
- **HIPAA**: Code must be HIPAA compliant. No PHI in codebase or logs.
- **Audit Trails**: All data access and model decisions should be loggable.
- **Bias**: Regularly check models for bias against protected groups.

## 2. Scientific Computing
- **Vectorization**: Prefer vectorized operations (`numpy`, `torch`) over loops.
- **Reproducibility**: Use fixed seeds for random number generators.
- **Data Versioning**: Track data versions with models (using DVC or MLflow).

## 3. PyTorch Best Practices
- **Modules**: Inherit from `nn.Module` or `LightningModule`.
- **Devices**: Write device-agnostic code (`.to(device)` or `register_buffer`).
- **DataLoading**: Use `DataLoader` with appropriate `num_workers`.
- **Validation**: Always validate input shapes and types in `forward`.

## 4. Workflow
- Use `nox` for consistent environments.
- Write tests before fixing bugs.
- Document assumptions clearly.
