# Hottopoteto Development Guide

## Quick Start

### Prerequisites

- Python 3.12+
- Git

### Development Environment Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd hottopoteto
```

2. **Create and activate virtual environment:**
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Verify installation:**
```bash
python -m pytest --version
python main.py --help
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=core --cov=plugins

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Generate HTML coverage report
pytest --cov=core --cov=plugins --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Organization

- `tests/unit/` - Unit tests for individual modules
- `tests/integration/` - Integration tests for complete workflows
- `tests/conftest.py` - Shared fixtures and configuration
- `pytest.ini` - pytest configuration and markers

### Writing Tests

Follow the patterns in existing test files:

```python
import pytest
from core.executor import RecipeExecutor

def test_executor_initialization():
    """Tests should have clear docstrings."""
    executor = RecipeExecutor()
    assert executor is not None
```

Use fixtures from `conftest.py`:
```python
def test_with_fixture(sample_recipe_yaml):
    """Use shared fixtures for consistent test data."""
    assert "steps" in sample_recipe_yaml
```

## Code Quality Standards

### Style Guidelines

- Follow PEP 8 conventions
- Use type hints for function signatures
- Document public APIs with docstrings
- Keep functions focused and testable

### Before Committing

1. Run tests: `pytest`
2. Check coverage: `pytest --cov=core --cov=plugins`
3. Verify code runs: `python main.py --help`

## Project Structure

```
hottopoteto/
├── core/                   # Core framework modules
│   ├── executor.py        # Recipe execution engine
│   ├── registry.py        # Function and domain registry
│   ├── domains.py         # Domain management
│   ├── templates.py       # Template rendering
│   └── schemas.py         # Schema validation
│
├── plugins/               # Plugin modules (LLM, storage, etc.)
│   ├── gemini/           # Google Gemini integration
│   └── mongodb/          # MongoDB storage plugin
│
├── templates/            # Recipe templates
│   └── recipes/         # YAML recipe definitions
│
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
│
└── docs/               # Documentation
    ├── guides/         # How-to guides
    ├── concepts/       # Architecture concepts
    └── reference/      # API reference
```

## Development Workflow

### Adding New Features

1. Create feature branch from `main`
2. Write tests first (TDD approach)
3. Implement feature
4. Verify tests pass with good coverage
5. Update documentation
6. Submit pull request

### Working with Recipes

Recipes are YAML files that define execution workflows:

```yaml
name: my-recipe
description: Example recipe
steps:
  - function: domain::function_name
    params:
      key: value
```

See `docs/guides/creating_recipes.md` for detailed guide.

### Working with Plugins

Create new plugins in `plugins/` directory with:
- `manifest.json` - Plugin metadata
- `links.py` - Function implementations
- `schemas/` - Pydantic schemas for validation

See `docs/guides/creating_plugins.md` for detailed guide.

## Troubleshooting

### Common Issues

**Import errors after installing dependencies:**
- Ensure virtual environment is activated
- Try reinstalling: `pip install -r requirements.txt --force-reinstall`

**Tests failing with import errors:**
- Check Python path includes project root
- Run from project root directory

**Coverage reports not generating:**
- Ensure `pytest-cov` is installed: `pip install pytest-cov`
- Check pytest output for coverage plugin errors

### Getting Help

- Check existing documentation in `docs/`
- Review ADRs in `docs/architecture/decisions/`
- Ask team for guidance

## Additional Resources

- [Architecture Overview](docs/concepts/architecture.md)
- [Creating Recipes](docs/guides/creating_recipes.md)
- [Creating Plugins](docs/guides/creating_plugins.md)
- [Schema Usage](docs/guides/using-schemae.md)
- [Contributing Guidelines](CONTRIBUTING.md)
