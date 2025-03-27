# Contributing to LLMGrep

Thank you for your interest in contributing to LLMGrep! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

## How to Contribute

### 1. Setting up Your Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/your-username/LLMgrep.git
cd LLMgrep

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Making Changes

1. Create a new branch:
    ```bash
    git checkout -b feature/your-feature-name
    ```
2. Make your changes
3. Write or update tests
4. Run tests locally:
    ```bash
    pytest tests/
    ```
5. Commit your changes:
    ```bash
    git commit -m "feat: description of your changes"
    ```

### 3. Pull Request Process

1. Update documentation if needed
2. Push to your fork
3. Submit a pull request to the `main` branch
4. Wait for review and address any feedback

## Code Standards

- Follow PEP 8 style guide
- Write meaningful commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
- Include docstrings for new functions/classes
- Add unit tests for new features

## Testing

- All new features must include tests
- Run the test suite before submitting PRs
- Maintain or improve code coverage

## Documentation

- Update README.md if adding new features
- Provide clear code comments
- Update API documentation when changing interfaces

## Issue Reporting

- Use the issue tracker for bugs and feature requests
- Check existing issues before creating new ones
- Include clear steps to reproduce bugs
- Provide system information when relevant

## License

By contributing to LLMGrep, you agree that your contributions will be licensed under the MIT License.