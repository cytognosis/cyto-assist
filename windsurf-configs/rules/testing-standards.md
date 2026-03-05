---
description: Testing standards for Healthcare AI applications
globs: ["tests/**/*.py"]
---
# Testing Standards

## Principles
1.  **Isolation**: Tests must not depend on external systems.
2.  **Safety**: Never use real patient data in tests.
3.  **Speed**: Unit tests should be fast (<100ms).

## Markers
- `@pytest.mark.unit`: Unit tests (fast).
- `@pytest.mark.integration`: Integration tests (slower).
- `@pytest.mark.gpu`: Tests requiring GPU.
- `@pytest.mark.slow`: Long running tests (>1s).
- `@pytest.mark.clinical`: Validation against clinical metrics.

## Synthetic Data
- Generate synthetic data that statistically resembles real data.
- Use `faker` or `hypothesis` for generating test cases.
- Validate synthetic data schema matching production schema.

## Coverage
- Minimum 80% coverage required.
- Critical paths (model inference, data processing) require 100%.
