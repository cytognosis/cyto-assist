---
description: Testing standards for Healthcare AI projects
globs: ["tests/**/*.py", "**/tests/*.py"]
---
# Testing Standards

## Principles
1.  **Coverage**: Aim for 80%+ code coverage.
2.  **Isolation**: Tests should not depend on external services (mock them).
3.  **Determinism**: Tests must be deterministic (seed RNGs).

## Test Types

### Unit Tests
- Small, fast tests for individual functions/classes.
- Use `pytest`.
- Mock external dependencies.

### Integration Tests
- Test interaction between components.
- Use standard datasets (synthetic or anonymized).

### Clinical Validation Tests
- Verify model performance against clinical benchmarks.
- Ensure fairness and bias checks are passed.
- **Marker**: `@pytest.mark.clinical`

### GPU Tests
- For ML models requiring acceleration.
- **Marker**: `@pytest.mark.gpu`

## Synthetic Data
- Use synthetic data for testing pipelines to avoid PHI exposure.
- `faker` or specialized generation tools should be used.

## Example
```python
import pytest
import torch

@pytest.mark.gpu
def test_model_forward_pass():
    model = MyModel().cuda()
    input_data = torch.randn(1, 3, 224, 224).cuda()
    output = model(input_data)
    assert output.shape == (1, 10)
```
