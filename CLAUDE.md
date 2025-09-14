# Claude Coding Standards

## Import Rules
- **Always use absolute imports** for project modules
  - ✅ `from src.models.point import Point`
  - ❌ `from .point import Point`
- Standard library imports first, then third-party, then project imports
- Use `isort` formatting for import organization

## Python Best Practices
- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and return types
- Write **docstrings** for all classes and public methods (Google style)
- Include proper **error handling** with specific exceptions
- Use descriptive variable and function names
- Prefer **properties** over getter/setter methods where appropriate

## Code Quality Standards
- Follow **black** formatting rules (line length: 88 characters)
- Follow **flake8** linting rules
- Follow **isort** import sorting rules
- Use **dataclasses** or **attrs** for simple data containers when appropriate
- Avoid magic numbers - use named constants
- Keep functions focused and small (single responsibility principle)

## Linting Commands
Run these commands before committing:
```bash
# Activate virtual environment
source venv/bin/activate

# Format code
black src/ tests/
isort src/ tests/

# Check linting
flake8 src/ tests/

# Run tests
pytest tests/
```

## Testing Standards
- Write unit tests for all public methods
- Use descriptive test method names
- Follow AAA pattern (Arrange, Act, Assert)
- Aim for >90% test coverage

## Documentation
- Use Google-style docstrings
- Document all public APIs
- Include type information in docstrings
- Provide examples for complex functions

## Error Handling
- Use specific exception types
- Provide meaningful error messages
- Validate inputs at public API boundaries
- Use logging for debugging information

## Project Structure
- Keep related functionality grouped in modules
- Use clear, descriptive module names
- Separate business logic from UI code
- Follow dependency injection principles