# Contributing to Flutter Localization Automation

Thank you for considering contributing to Flutter Localization Automation! 🎉

## How to Contribute

### 🐛 Reporting Issues

If you encounter bugs or issues:

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - Flutter version
   - Complete error messages
   - Steps to reproduce
   - Sample code if applicable

### 🚀 Suggesting Features

We welcome feature suggestions! Please:

1. **Check if the feature already exists** in issues or discussions
2. **Describe the use case** - what problem does it solve?
3. **Provide examples** of how it would work
4. **Consider backward compatibility**

### 💻 Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YourUsername/flutter-localization-automation.git
   cd flutter-localization-automation
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

1. **Follow PEP 8** Python style guidelines
2. **Add type hints** for function parameters and return values
3. **Write docstrings** for all functions and classes
4. **Add error handling** for file operations and edge cases
5. **Include logging** for debugging and user feedback
6. **Write tests** for new functionality

#### Code Structure

- `flutter_localization_automation.py` - Main localization tool
- `fix_localization_issues.py` - Post-processing fixes
- `examples/` - Example usage and ARB files
- `tests/` - Test files
- `docs/` - Additional documentation

#### Testing

Before submitting:

1. **Test with different project structures**
2. **Test with various ARB file formats**
3. **Verify the tool doesn't break existing functionality**
4. **Run on both small and large projects**

#### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update README.md** if adding new features
5. **Submit pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/examples if applicable

## Development Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/YourUsername/flutter-localization-automation.git
cd flutter-localization-automation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 .
```

### Testing with Flutter Projects

Create a test Flutter project:

```bash
flutter create test_project
cd test_project

# Add some hardcoded strings to test
# Run the localization tool
python ../flutter_localization_automation.py --dry-run
```

## Code Style Guidelines

### Python Code Style

- Use **4 spaces** for indentation
- **Maximum line length**: 88 characters
- Use **meaningful variable names**
- Add **type hints** for all functions
- Use **f-strings** for string formatting
- Follow **PEP 8** conventions

### Documentation Style

- Use **Google-style docstrings**
- Include **parameter descriptions**
- Add **usage examples** where helpful
- Keep **README.md** up to date

### Example Function

```python
def process_arb_file(file_path: str, encoding: str = 'utf-8') -> Dict[str, str]:
    """
    Process an ARB file and return translations.
    
    Args:
        file_path: Path to the ARB file
        encoding: File encoding (default: utf-8)
        
    Returns:
        Dictionary mapping keys to translated strings
        
    Raises:
        FileNotFoundError: If the ARB file doesn't exist
        ValueError: If the ARB file format is invalid
        
    Example:
        >>> translations = process_arb_file('app_en.arb')
        >>> print(translations['welcome'])
        'Welcome'
    """
    # Implementation here
```

## Community Guidelines

### Be Respectful

- Use welcoming and inclusive language
- Be respectful of different viewpoints and experiences
- Give and receive constructive feedback gracefully
- Focus on what's best for the community

### Stay On Topic

- Keep discussions relevant to Flutter localization
- Use appropriate channels for different types of discussions
- Help keep the project focused and organized

## Recognition

Contributors will be:

- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes** for significant contributions
- **Invited to the contributors team** for ongoing contributors

## Questions?

- 📧 **Email**: Open an issue for questions
- 💬 **Discussions**: Use GitHub Discussions for general questions
- 🐛 **Issues**: Use GitHub Issues for bugs and feature requests

---

**Thank you for helping make Flutter localization easier for everyone!** 🙏
