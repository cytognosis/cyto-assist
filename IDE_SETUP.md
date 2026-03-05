# IDE Setup Guide for cyto-assist

This guide provides comprehensive setup instructions for VS Code, Cursor, and Windsurf IDEs optimized for healthcare AI development.

## 🎯 Overview

This project includes optimized configurations for three popular IDEs:
- **VS Code**: Microsoft's popular open-source editor
- **Cursor**: AI-powered code editor with advanced AI features
- **Windsurf**: Next-generation AI IDE with Cascade assistant

All three IDEs share common configurations where possible, with specialized features for each.

## 📁 Configuration Files Structure

```
cyto-assist/
├── .vscode/                    # Shared VS Code configurations
│   ├── settings.json          # Editor settings and preferences
│   ├── extensions.json        # Recommended extensions
│   ├── tasks.json            # Build and development tasks
│   └── launch.json           # Debug configurations
├── .cursor/                   # Cursor-specific configurations
│   └── rules/                # AI coding rules
│       ├── python-healthcare-ai.md
│       ├── testing-standards.md
│       └── documentation.md
├── windsurf-configs/         # Windsurf configurations (copy to .windsurf/)
│   ├── rules/               # AI coding rules
│   └── README.md           # Setup instructions
├── .cascade.js              # Windsurf Cascade AI configuration
├── .editorconfig           # Cross-IDE editor configuration
├── .cursorignore          # Cursor context exclusions
├── .codeiumignore         # Windsurf/Codeium indexing exclusions
└── .cursorindexingignore  # Cursor indexing exclusions
```

## 🚀 Quick Setup

### 1. VS Code Setup
```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker

# Open project
code .
```

### 2. Cursor Setup
```bash
# Open project in Cursor
cursor .

# Rules are automatically detected from .cursor/rules/
# Verify in Cursor Settings > Rules
```

### 3. Windsurf Setup
```bash
# Copy Windsurf configurations
cp -r windsurf-configs/rules .windsurf/

# Open project in Windsurf
windsurf .

# Verify rules in Cascade customization panel
```

## 🔧 Shared Configurations

### .vscode/settings.json
**Shared across all IDEs** - Contains:
- Python interpreter configuration
- Formatting and linting settings
- File associations and exclusions
- Jupyter notebook settings- Healthcare compliance settings
### .vscode/extensions.json
**Recommended extensions** for all IDEs:
- **Python Development**: python, ruff, mypy-type-checker
- **Configuration**: even-better-toml, vscode-yaml
- **Git**: gitlens, vscode-pull-request-github
- **Documentation**: markdown-all-in-one, vscode-markdownlint
- **Jupyter**: jupyter, jupyter-keymap, jupyter-renderers- **ML/AI**: tensorboard
### .vscode/tasks.json
**Development tasks** integrated with nox:
- `Initialize Project` - Set up development environment
- `Run Tests` - Execute full test suite
- `Format Code` - Auto-format with ruff
- `Lint Code` - Check code quality
- `Security Scan` - Run security analysis
- `Clinical Compliance Tests` - HIPAA and clinical validation- `GPU Tests` - ML model testing
### .vscode/launch.json
**Debug configurations**:
- Python: Current File
- Python: Module (cyto_assist)
- Python: Tests (pytest)
- Python: Clinical Tests- Python: GPU Tests
### .editorconfig
**Cross-IDE editor settings**:
- 4-space indentation for Python
- 2-space indentation for YAML/JSON
- 119 character line length
- UTF-8 encoding, LF line endings
- Trailing whitespace trimming

## 🤖 AI-Specific Configurations

### Cursor Rules (.cursor/rules/)

#### python-healthcare-ai.md
- Healthcare compliance requirements
- Scientific computing best practices
- PyTorch/deep learning guidelines- Testing requirements with healthcare markers
- Documentation standards (NumPy format)
- Security practices for healthcare data

#### testing-standards.md
- Comprehensive testing guidelines
- Healthcare-specific test markers
- Synthetic data generation
- ML model testing procedures- Coverage requirements (80% minimum)
- Property-based testing with hypothesis

#### documentation.md
- NumPy docstring format requirements
- API documentation with Sphinx
- Healthcare compliance documentation- Scientific documentation standards
- Jupyter notebook documentation
### Windsurf Rules (.windsurf/rules/)

#### healthcare-ai-development.md
- Comprehensive development guidelines
- HIPAA compliance requirements- Scientific computing best practices
- PyTorch optimization guidelines- Development workflow integration

#### testing-standards.md
- Testing philosophy and organization
- Healthcare data testing with synthetic data
- ML model testing procedures- Coverage requirements and reporting
- Property-based testing guidelines

#### documentation-standards.md
- Documentation philosophy and requirements
- NumPy docstring format with examples
- API documentation structure
- Healthcare compliance documentation- Scientific documentation standards

#### security-compliance.md
- Security-first development principles
- HIPAA compliance requirements- Data privacy and protection measures
- Secure coding practices
- Vulnerability management

### .cascade.js (Windsurf)
**AI behavior configuration**:
- Project context and domain awareness
- Healthcare-specific priorities
- Code generation preferences
- ML/AI optimization settings- Custom commands and shortcuts

## 🔍 Ignore Files Configuration

### .cursorignore
**Excludes from Cursor context**:
- Build artifacts and cache directories
- Large experiment files- Notebook outputs- Virtual environments and dependencies

### .codeiumignore
**Excludes from Windsurf/Codeium indexing**:
- Same patterns as .cursorignore
- Optimized for Windsurf's indexing system

### .cursorindexingignore
**Excludes from Cursor indexing only**:
- Large binary files and data
- Generated documentation
- Cache and temporary files

## 🛠️ Development Workflow

### Daily Development
1. **Start development**: `nox -s init_project`
2. **Quick testing**: `nox -s test_fast`
3. **Format code**: `nox -s format`
4. **Check quality**: `nox -s lint`
5. **Full validation**: `nox -s ci`

### Healthcare Compliance
1. **Clinical tests**: `nox -s test_clinical`
2. **HIPAA validation**: `nox -s test_hipaa`
3. **Security scan**: `nox -s security`
4. **Audit logs**: Check comprehensive logging
### ML/AI Development
1. **GPU tests**: `nox -s test_gpu`
2. **Model validation**: Run performance benchmarks
3. **Training workflows**: Use PyTorch Lightning patterns
4. **Inference testing**: Validate model outputs
## 🎨 Theme and Appearance

### Recommended Themes
- **VS Code**: GitHub Dark/Light themes
- **Cursor**: Built-in themes with AI-optimized syntax highlighting
- **Windsurf**: Cytognosis-inspired themes (if available)

### Font Recommendations
- **Primary**: JetBrains Mono, Fira Code, Cascadia Code
- **Accessibility**: Fonts with good dyslexia support
- **Size**: 14px minimum for accessibility

## 🔧 Troubleshooting

### Common Issues

#### Extensions Not Loading
```bash
# VS Code
code --list-extensions
code --install-extension <extension-id>

# Cursor
# Check Extensions panel and install manually
```

#### Python Interpreter Not Found
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Update VS Code settings
"python.defaultInterpreterPath": "./.venv/bin/python"
```

#### AI Rules Not Working
- **Cursor**: Check Settings > Rules for rule detection
- **Windsurf**: Verify .windsurf/rules/ directory exists and is readable
- **Both**: Restart IDE after adding new rules

#### Linting/Formatting Issues
```bash
# Reinstall development dependencies
nox -s init_project

# Check tool configurations
ruff check .
mypy src/
```

## 📚 Additional Resources

- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [Cursor Documentation](https://docs.cursor.com/)
- [Windsurf Documentation](https://docs.windsurf.com/)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/for-professionals/security/guidance/index.html)- [PyTorch Best Practices](https://pytorch.org/tutorials/beginner/former_torchies/nnft_tutorial.html)
## 🤝 Team Collaboration

### Shared Configurations
- **Include in VCS**: .vscode/, .cursor/, .editorconfig, .cascade.js
- **Team Setup**: All team members should use same IDE configurations
- **Updates**: Coordinate configuration changes through pull requests

### Individual Preferences
- **Personal Settings**: Keep in user/global settings, not workspace
- **Extensions**: Additional extensions beyond recommended set
- **Themes**: Personal preference, not enforced

---

**Note**: This setup is optimized for cyto-assist and healthcare AI development. Adjust configurations as needed while maintaining compliance and security standards.
