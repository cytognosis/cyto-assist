# Notebooks Directory

This directory contains Jupyter notebooks for cyto-assist.

## Structure

```
notebooks/
├── exploratory/      # Data exploration and analysis
├── preprocessing/    # Data cleaning and preparation
├── modeling/         # Model development and validation
├── evaluation/       # Results analysis and visualization
└── reports/         # Final reports and presentations
```

## Guidelines

### Naming Convention
- Use descriptive names: `01_data_exploration.ipynb`
- Include sequence numbers for workflow order
- Use underscores, not spaces

### Best Practices
- Clear markdown explanations for each section
- Remove output before committing (use nbstripout)
- Include data source documentation
- Follow HIPAA compliance for clinical data

### Clinical Data Handling
## Setup

Install notebook dependencies:
```bash
pip install -e ".[notebooks]"
```

Start JupyterLab:
```bash
jupyter lab
```
