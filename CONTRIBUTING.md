# Contributing to cyto-assist

Thank you for your interest in contributing to cyto-assist! This project is part of the Cytognosis Foundation's mission to advance AI-native technology for preventive healthcare and disease detection.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for all contributors.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [issue tracker](https://github.com/cytognosis/cyto-assist/issues) to avoid duplicates.

When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs. actual behavior**
- **Environment details** (OS, Python version, package versions)
- **Code samples** or test cases if applicable
- **Error messages** and stack traces

**Important**: Never include Protected Health Information (PHI) or real patient data in bug reports. Use synthetic or anonymized data only.
### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide detailed description** of the proposed functionality
- **Explain why this enhancement would be useful**
- **Include examples** of how it would be used
- **Consider backwards compatibility**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Set up your development environment**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cyto-assist.git
   cd cyto-assist
   nox -s init_project
   ```

3. **Make your changes**:
   - Write clear, documented code
   - Follow the project's coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**:
   ```bash
   nox -s test        # Run full test suite
   nox -s lint        # Check code quality
   nox -s format      # Format code
nox -s security    # Run security checks
nox -s ci          # Run complete CI pipeline
   ```

5. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Follow [Conventional Commits](https://www.conventionalcommits.org/) format
   - Reference relevant issues

6. **Push to your fork** and submit a pull request

## Development Guidelines

### Code Style

- **Python version**: Python 3.10+
- **Line length**: 119 characters (configured in `.ruff.toml`)
- **Type hints**: Required for all public functions
- **Docstrings**: NumPy format for all public APIs
- **Formatting**: Automated with Ruff (run `nox -s format`)

### Testing Standards

- **Coverage**: Maintain >80% test coverage
- **Test types**: Unit tests, integration tests, property-based tests
- **Healthcare markers**: Use `@pytest.mark.clinical` and `@pytest.mark.hipaa` for compliance tests
- **GPU tests**: Mark with `@pytest.mark.gpu` for GPU-dependent tests
- **Synthetic data**: Never use real patient data in tests

### Documentation

- **API documentation**: Auto-generated from docstrings using Sphinx
- **User guides**: Written in Markdown in `docs/`
- **Examples**: Include runnable examples in docstrings
- **Changelog**: Update `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/)

### Healthcare Compliance

This project handles healthcare data and must maintain strict compliance standards:

- **HIPAA Compliance**: All code must be HIPAA-compliant
- **Data Privacy**: Implement privacy-by-design principles
- **Security**: No hardcoded credentials, proper encryption, secure data handling
- **Audit Logging**: Maintain comprehensive audit trails for data access
- **PHI Protection**: Never log, print, or expose Protected Health Information

Run compliance checks:
```bash
nox -s test_clinical  # Clinical compliance tests
nox -s test_hipaa     # HIPAA compliance validation
nox -s security       # Security scanning
```
### Scientific Rigor

- **Reproducibility**: All experiments must be reproducible with fixed random seeds
- **Validation**: Include statistical validation of results
- **Documentation**: Document methodology, assumptions, and limitations
- **References**: Cite relevant literature and prior work

## Development Workflow

### Setting Up Your Environment

```bash
# Clone the repository
git clone https://github.com/cytognosis/cyto-assist.git
cd cyto-assist

# Initialize development environment
nox -s init_project

# Install pre-commit hooks
pre-commit install
```

### Daily Development

```bash
# Make changes to code
# ...

# Run fast tests during development
nox -s test_fast

# Format and lint code
nox -s format
nox -s lint

# Run full test suite before committing
nox -s test

# Run complete CI pipeline
nox -s ci
```

### Branching Strategy

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/*`**: New features
- **`bugfix/*`**: Bug fixes
- **`hotfix/*`**: Urgent production fixes

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `security`: Security improvements
- `compliance`: Compliance-related changes
## Review Process

1. **Automated checks**: All CI checks must pass
2. **Code review**: At least one maintainer approval required
3. **Testing**: Comprehensive test coverage
4. **Compliance review**: Healthcare compliance verification
5. **Documentation**: Updated documentation and changelog

## Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Email**: [dev@cytognosis.org](mailto:dev@cytognosis.org) for general inquiries

### Recognition

Contributors are recognized in:
- [ATTRIBUTION.md](ATTRIBUTION.md)
- GitHub contributors page
- Release notes for significant contributions

## License

By contributing to cyto-assist, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

If you have questions about contributing, please:
- Check the [documentation](https://cyto-assist.readthedocs.io)
- Open a [GitHub Discussion](https://github.com/cytognosis/cyto-assist/discussions)
- Email [dev@cytognosis.org](mailto:dev@cytognosis.org)

Thank you for contributing to advancing healthcare through open science! 🏥🔬✨
