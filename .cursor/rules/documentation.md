---
description: Documentation standards for Python code
globs: ["**/*.py", "**/*.md", "**/*.rst"]
---
# Documentation Standards

## Docstrings
- Use **Google Style** docstrings.
- Every public module, class, and function must have a docstring.
- Include `Args`, `Returns`, `Raises`, and `Examples`.

### Example
```python
def calculate_risk_score(patient_data: dict) -> float:
    """Calculates the risk score for a patient.

    Args:
        patient_data (dict): A dictionary containing patient metrics.
            Must include 'age' and 'blood_pressure'.

    Returns:
        float: The calculated risk score between 0.0 and 1.0.

    Raises:
        ValueError: If required keys are missing from patient_data.
    """
    pass
```

## READMEs
- All major directories should have a `README.md`.
- Explain the purpose of the directory and key files.

## Sphinx Documentation
- API reference is generated automatically.
- Write tutorials in Markdown (`myst-nb`) or Jupyter Notebooks.
- Keep `IDE_SETUP.md` updated if tooling changes.
