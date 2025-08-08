# Contributing to InstanceHub

Thank you for your interest in contributing to InstanceHub! This document provides guidelines and information for contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/instancehub.git
   cd instancehub
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** and ensure they follow our coding standards
3. **Run tests**:
   ```bash
   python -m pytest tests/ -v
   ```
4. **Commit your changes**:
   ```bash
   git commit -m "Add: your feature description"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub

## Coding Standards

- Follow **PEP 8** Python style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for all functions and classes
- Keep functions **small and focused**
- Use **meaningful variable and function names**

## Code Formatting

We use the following tools for code quality:

```bash
# Format code
black instancehub/

# Check style
flake8 instancehub/

# Type checking
mypy instancehub/
```

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage
- Use descriptive test names

## Commit Message Format

Use clear and descriptive commit messages:

- `Add: new feature description`
- `Fix: bug description`
- `Update: change description`
- `Remove: removed feature description`
- `Docs: documentation changes`

## Pull Request Guidelines

1. **Describe your changes** clearly in the PR description
2. **Reference any related issues** using `#issue-number`
3. **Include screenshots** if your changes affect the UI
4. **Ensure all tests pass**
5. **Update documentation** if needed

## Feature Requests

We welcome feature requests! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the feature** and its use case
3. **Explain why it would be valuable**
4. **Consider implementation complexity**

## Bug Reports

When reporting bugs, please include:

1. **Steps to reproduce** the issue
2. **Expected behavior**
3. **Actual behavior**
4. **Environment details** (OS, Python version, etc.)
5. **Error messages** or logs if applicable

## Areas for Contribution

We're particularly interested in contributions for:

- **New cloud providers** (Azure, GCP)
- **Additional monitoring metrics**
- **Service integrations**
- **Performance improvements**
- **Documentation improvements**
- **Test coverage**

## Questions?

If you have questions about contributing, feel free to:

- **Open an issue** for discussion
- **Join our community** discussions
- **Contact the maintainers**

Thank you for contributing to InstanceHub! 🚀
