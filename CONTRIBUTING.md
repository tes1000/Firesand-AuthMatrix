# Contributing to Firesands Auth Matrix

Thank you for your interest in contributing to Firesands Auth Matrix! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/FiresandsAuthMatrix.git
   cd FiresandsAuthMatrix/python
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Project Structure

Understanding the project structure will help you contribute effectively:

```
python/
├── Firesand_Auth_Matrix.py      # Main entry point
├── UI/                          # GUI components
│   ├── UI.py                   # Main UI controller
│   ├── components/             # Reusable UI components
│   └── views/                  # Application views/tabs
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

### Running the Application

```bash
python Firesand_Auth_Matrix.py
```

## Making Changes

### Before You Start

1. **Check existing issues** to see if your idea is already being worked on
2. **Create an issue** to discuss major changes before implementing
3. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in existing functionality
- **Feature additions**: Add new capabilities
- **Documentation**: Improve or add documentation
- **Performance improvements**: Optimize existing code
- **UI/UX improvements**: Enhance user experience
- **Tests**: Add or improve test coverage

## Submitting Changes

### Commit Guidelines

1. **Write clear commit messages**:
   ```
   feat: add support for OAuth authentication
   
   - Implement OAuth flow for user authentication
   - Add OAuth configuration options to UI
   - Update documentation with OAuth setup instructions
   ```

2. **Use conventional commit format**:
   - `feat:` new features
   - `fix:` bug fixes
   - `docs:` documentation changes
   - `style:` formatting changes
   - `refactor:` code restructuring
   - `test:` adding tests
   - `chore:` maintenance tasks

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update the README** if you've added new features
5. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Testing instructions

### Pull Request Template

```markdown
## Description
Brief description of the changes.

## Related Issues
Fixes #issue_number

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] I have tested these changes locally
- [ ] I have added appropriate test cases
- [ ] All existing tests pass

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context.
```

## Style Guidelines

### Python Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for functions and classes
- Keep functions focused and reasonably sized
- Use meaningful variable and function names

### Example Code Style

```python
def convert_postman_to_authmatrix(postman_data: dict) -> dict:
    """Convert a Postman collection to AuthMatrix format.
    
    Args:
        postman_data: Dictionary containing Postman collection data
        
    Returns:
        Dictionary in AuthMatrix format
        
    Raises:
        ValueError: If postman_data is invalid
    """
    if not isinstance(postman_data, dict):
        raise ValueError("postman_data must be a dictionary")
    
    # Implementation here...
    return authmatrix_spec
```

### UI/UX Guidelines

- Follow **Qt/PySide6** best practices
- Maintain **consistent styling** with existing UI
- Ensure **accessibility** (keyboard navigation, screen readers)
- Test on different **screen sizes**
- Use **clear and concise** text

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_specific_file.py
```

### Writing Tests

- Write tests for new functionality
- Include edge cases and error conditions
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)

```python
def test_convert_postman_collection_with_bearer_auth():
    """Test conversion of Postman collection with bearer authentication."""
    # Arrange
    postman_data = {
        "info": {"name": "Test Collection"},
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "test-token"}]
        },
        "item": [...]
    }
    
    # Act
    result = convert_postman_to_authmatrix(postman_data)
    
    # Assert
    assert result["roles"]["admin"]["auth"]["type"] == "bearer"
    assert result["roles"]["admin"]["auth"]["token"] == "test-token"
```

## Areas for Contribution

Here are some areas where contributions are especially welcome:

### High Priority
- **Authentication methods**: OAuth, API keys, custom headers
- **Test reporting**: Export results to various formats
- **Performance**: Optimize large collection handling
- **Error handling**: Better error messages and recovery

### Medium Priority
- **UI improvements**: Better responsive design, dark theme
- **Documentation**: More examples, video tutorials
- **Internationalization**: Support for multiple languages
- **Integration**: CI/CD pipeline integration

### Low Priority
- **Advanced features**: Custom scripting, plugin system
- **Analytics**: Test result analysis and trends
- **Mobile support**: Touch-friendly interface

## Questions and Support

If you have questions about contributing:

1. **Check the documentation** first
2. **Search existing issues** for similar questions
3. **Create a new issue** with the "question" label
4. **Join discussions** in existing issues

## Recognition

Contributors will be recognized in:
- The project README
- Release notes for significant contributions
- GitHub contributors page

Thank you for contributing to Firesands Auth Matrix! 🎉