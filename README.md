# cyto-assist

[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]
[![License][badge-license]][license]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/cytognosis/cyto-assist/test.yaml?branch=main
[badge-docs]: https://readthedocs.org/projects/cyto-assist/badge/?version=latest
[badge-license]: https://img.shields.io/github/license/cytognosis/cyto-assist
> ✨ CRUFT UPDATE TEST: Successful!

Personal assistant and AI scientist project

## About Cytognosis Foundation

This project is part of the [Cytognosis Foundation](https://cytognosis.org) initiative to advance AI-native technology for preventive healthcare and disease detection. Our mission is to develop accessible, scientifically rigorous tools that empower researchers and clinicians to improve human health through cellular diagnostics and precision medicine.

### Our Values

- **Scientific Rigor**: Evidence-based approaches with reproducible results
- **Healthcare Accessibility**: Open science and equitable access to technology
- **Data Privacy**: HIPAA-compliant, privacy-first design
- **Collaboration**: Community-driven development and knowledge sharing
- **Innovation**: Cutting-edge AI/ML techniques for healthcare challenges

### Core Technology Stack

This template is proudly powered by state-of-the-art open source infrastructure:

- **[Cytognosis Cookiecutter](https://cytognosis.github.io/cookiecutter/)**: The underlying architectural template
- **[Cytoskeleton](https://cytognosis.github.io/cytoskeleton/)**: Component-based dependency injection framework
- **[Astral `uv`](https://github.com/astral-sh/uv)**: Blazing fast Python packaging and resolution
- **[Nox](https://nox.thea.codes/)**: Flexible test and interactive session orchestration
- **[Cruft](https://cruft.github.io/cruft/)**: Automated template synchronization and delta tracking
- **[PyTorch](https://pytorch.org)**: Deep Learning framework strictly bound to rocm
- **[Quarto](https://quarto.org/) & [Marimo](https://marimo.io/)**: Reactive, reproducible computational tutorials
- **[Sphinx](https://www.sphinx-doc.org/)**: Standardized auto-documentation generation for Google-style docstrings

## Getting started

Please refer to the [documentation][],
in particular, the [API documentation][].

## Installation

You need to have Python 3.10 or newer installed on your system.
If you don't have Python installed, we recommend installing [uv][].

There are several alternative options to install cyto-assist:

<!--
1) Install the latest release of `cyto-assist` from [PyPI][]:

```bash
pip install cyto-assist
```
-->

1. Install the latest development version:

```bash
pip install git+https://github.com/cytognosis/cyto-assist.git@main
```

## Development

This project uses [nox][] for automated development tasks. Nox provides a consistent, reproducible development environment with comprehensive tooling for healthcare AI development.

### Quick Start

```bash
# Clone the repository
git clone --recursive https://github.com/cytognosis/cyto-assist.git
cd cyto-assist

# Initialize the development environment
nox -s init_project

# Run tests
nox -s test

# Format code
nox -s format

# Run linting
nox -s lint
```

### Interactive Tutorials & Notebooks

Cytognosis enforces rigorous, reactive notebooks for clinical data provenance. Use our provided templates:

```bash
# Preview Quarto HTML Notebooks (docs/notebooks/tutorial.qmd)
nox -s quarto_preview

# Launch Marimo Reactive Editor (docs/notebooks/tutorial.py)
nox -s marimo_edit

# Launch Standard Jupyter Lab
nox -s jupyter_lab
```

### Resource Allocation

You can strictly limit hardware usage (Memory, CPU masks, APU overrides) during any Nox session by exporting `CYTO_LIMIT_*` variables. For example:

```bash
CYTO_LIMIT_CPUS=8 CYTO_LIMIT_GPUS=1 nox -s test
HSA_OVERRIDE_GFX_VERSION=10.3.0 nox -s jupyter_lab
```

### Available Nox Sessions

#### Core Development

- **`init_project`** - Initialize the project environment with all dependencies
- **`test`** - Run the full test suite with coverage reporting
- **`test_fast`** - Run tests without coverage for faster feedback
- **`lint`** - Run linting (ruff) and type checking (mypy)
- **`format`** - Format code with ruff and fix import issues
- **`security`** - Run security scans (bandit, safety)
- **`ci`** - Run the complete CI pipeline locally

#### Healthcare Compliance

- **`test_clinical`** - Run clinical compliance tests
- **`test_hipaa`** - Run HIPAA compliance validation tests

#### ML/AI Development

- **`test_gpu`** - Run GPU-accelerated tests (requires CUDA)

#### Documentation

- **`docs`** - Build documentation with Sphinx
- **`docs_serve`** - Build and serve documentation locally

#### Utilities

- **`clean`** - Clean build artifacts and caches
- **`update_deps`** - Update all dependencies
- **`pre_commit`** - Run pre-commit hooks
- **`jupyter`** - Start Jupyter Lab for interactive development
- **`build`** - Build the package for distribution

### Development Workflow

1. **Initialize your environment**:

   ```bash
   nox -s init_project
   ```

2. **Make your changes** and run tests frequently:

   ```bash
   nox -s test_fast  # Quick feedback
   nox -s test       # Full test suite
   ```

3. **Format and lint your code**:

   ```bash
   nox -s format     # Auto-format code
   nox -s lint       # Check for issues
   ```

4. **Run the full CI pipeline** before committing:

   ```bash
   nox -s ci
   ```

### Healthcare Compliance

For clinical and research projects, additional compliance checks are available:

```bash
# Run clinical compliance tests
nox -s test_clinical

# Run HIPAA compliance validation
nox -s test_hipaa

# Run comprehensive security scanning
nox -s security
```

### Configuration

The project uses separate configuration files for each tool:

- **`.ruff.toml`** - Ruff linting and formatting
- **`.mypy.ini`** - MyPy type checking
- **`.pytest.ini`** - Pytest configuration
- **`.pre-commit-config.yaml`** - Pre-commit hooks

All tools are configured with healthcare-specific rules and optimizations for research projects.

### Cache Management

Nox automatically manages caches in the `scratch/cache/` directory:

- Tool caches (mypy, pytest, ruff)
- Coverage reports
- Build artifacts
- Jupyter configurations
To clean all caches: `nox -s clean`

## Release notes

See the [changelog][].

## Contact

For questions and help requests:

- **General inquiries**: [dev@cytognosis.org](mailto:dev@cytognosis.org)
- **Bug reports**: Use the [issue tracker][]
- **Community discussions**: [Cytognosis Community Forum](https://community.cytognosis.org)
- **Security issues**: [security@cytognosis.org](mailto:security@cytognosis.org)

## Citation

If you use this software in your research, please cite:

```bibtex
@software{{cookiecutter.project_name}},
  author = {{cookiecutter.author_full_name}}},
  title = {{cookiecutter.project_name}}: {{cookiecutter.project_description}}},
  year = {{% now 'utc', '%Y' %}}},
  publisher = {Cytognosis Foundation},
  url = {https://github.com/{{cookiecutter.github_user}}/{{cookiecutter.github_repo}}}
}
```

## Acknowledgments

This project is developed with support from the Cytognosis Foundation and contributions from the open-source community. See [ATTRIBUTION.md](ATTRIBUTION.md) for detailed acknowledgments.

[uv]: https://github.com/astral-sh/uv
[nox]: https://nox.thea.codes/
[issue tracker]: https://github.com/cytognosis/cyto-assist/issues
[tests]: https://github.com/cytognosis/cyto-assist/actions/workflows/test.yaml
[documentation]: https://cyto-assist.readthedocs.io
[changelog]: https://cyto-assist.readthedocs.io/en/latest/changelog.html
[api documentation]: https://cyto-assist.readthedocs.io/en/latest/api.html
[license]: https://github.com/cytognosis/cyto-assist/blob/main/LICENSE
