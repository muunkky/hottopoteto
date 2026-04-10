# Contributing to Hottopoteto

Thank you for your interest in contributing to Hottopoteto! This guide provides information on how to contribute to the project.

## Code of Conduct

Please follow our code of conduct in all your interactions with the project.

## How Can I Contribute?

There are many ways to contribute:

- **Reporting Bugs**: Report bugs by creating an issue
- **Suggesting Features**: Suggest new features or improvements
- **Writing Code**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve documentation or add examples
- **Testing**: Write tests or improve existing tests

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/hottopoteto.git`
3. Create a new branch: `git checkout -b your-branch-name`
4. Make your changes
5. Test your changes
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin your-branch-name`
8. Submit a pull request

## Development Environment

Set up your development environment:

```bash
# Install dependencies
pip install -r requirements.txt

# Install recommended development tools
pip install pytest black mypy pytest-cov flake8
```

While we don't have a separate `requirements-dev.txt` yet, these tools are recommended for development.

## Core Design Principles

When contributing to Hottopoteto, please keep these principles in mind:

1. **Domain Isolation**: Links should be limited to using components from a single domain
2. **Cross-Domain Communication**: Use core infrastructure for cross-domain interactions
3. **Output Constraints**: Links should only write to their domain output folder or root output
4. **Recipe Composition**: Recipes are the primary way to combine functionality across domains
5. **Template Referencing**: Only recipe templates should reference other templates
6. **Credential Security**: Never store sensitive information in code or configuration files

See our [Core Principles](docs/core/principles.md) document for detailed explanations.

## Quick Architecture Overview

Hottopoteto has a few key concepts worth understanding:

### Domains

Domains represent knowledge areas with specialized data models and functions:
- **Models**: Define data structures for the domain (e.g., `LLMMessage`, `StorageEntity`)
- **Functions**: Implement domain operations (e.g., `generate_text`, `save_entity`)
- **Links**: Provide recipe integration for domain operations

### Links

Links are the building blocks of recipes:
- Each link has a **type** (e.g., `llm`, `storage.save`)
- Links take **inputs** and produce **outputs**
- Links are connected through a shared **context**

### Plugins

Plugins extend Hottopoteto with:
- New link types
- Domain implementations
- Specialized functionality

For more details, see the [Architecture Document](docs/ARCHITECTURE.md).

## Project Structure

```
hottopoteto/
├── core/                  # Core system components
├── domains/               # Domain implementations
├── plugins/               # Plugin implementations
├── utils/                 # Utility functions and helpers
├── cli/                   # Command-line interface components
├── recipes/               # Recipe definitions
└── storage/               # Storage system
```

## Contribution Guidelines

### Code Style

**Follow PEP 8 style guidelines strictly:**

- Use type hints for function signatures:
  ```python
  def process_recipe(recipe: dict, context: dict) -> dict:
      """Process a recipe and return results."""
      pass
  ```
  
- Write docstrings for all public APIs:
  ```python
  def my_function(param: str) -> bool:
      """
      Brief one-line summary.
      
      Args:
          param: Description of parameter
          
      Returns:
          Description of return value
          
      Raises:
          ValueError: When param is invalid
      """
      pass
  ```

- Keep lines under 100 characters
- Use 4 spaces for indentation (no tabs)
- Organize imports: stdlib → third-party → local

**Code Quality Checklist:**
- [ ] Type hints on all function signatures
- [ ] Docstrings on public functions/classes
- [ ] No hardcoded credentials or secrets
- [ ] Error handling for edge cases
- [ ] Logging added for debugging (use Python logging module)

**Before Committing:**
```bash
# Run tests
pytest

# Check coverage
pytest --cov=core --cov=plugins --cov-report=term

# Verify code runs
python main.py --help
```

### Documentation

- Update documentation when changing code
- Add examples for new features
- Use Markdown for documentation files

### Testing

**Testing is required for all contributions.** Follow these standards:

- **Write tests first** (TDD approach preferred)
- **All new features must have tests** with meaningful assertions
- **Bug fixes must include regression tests** to prevent reoccurrence
- **Aim for 50%+ code coverage** for new modules
- **Use pytest** exclusively for test framework

**Test Organization:**
- Unit tests → `tests/unit/`
- Integration tests → `tests/integration/`
- Use existing fixtures from `tests/conftest.py`
- Mark tests appropriately: `@pytest.mark.unit`, `@pytest.mark.integration`

**Running Tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=plugins

# Run specific types
pytest -m unit              # Unit tests only
pytest -m "not slow"        # Skip slow tests
```

**Example Test:**
```python
import pytest
from core.executor import RecipeExecutor

def test_executor_initialization():
    """Test executor creates successfully with default config."""
    executor = RecipeExecutor()
    assert executor is not None
    assert hasattr(executor, 'execute')

def test_with_fixture(sample_recipe_yaml):
    """Use shared fixtures for consistent test data."""
    assert "steps" in sample_recipe_yaml
    assert isinstance(sample_recipe_yaml["steps"], list)
```

**Code Coverage Requirements:**
- New modules should have 50%+ coverage
- Critical paths must be tested
- Edge cases should have explicit tests
- Use `--cov-report=html` to identify gaps

### Commit Messages

**Use Conventional Commits format:**

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**

```bash
# Simple feature commit
git commit -m "feat(domains): add LLM streaming support"

# Bug fix with body
git commit -m "fix(executor): handle missing context keys" \
           -m "" \
           -m "Previously crashed when optional context keys were missing" \
           -m "Now uses default values and logs warning"

# Breaking change
git commit -m "feat(registry)!: change domain registration API" \
           -m "" \
           -m "BREAKING CHANGE: register_domain now requires manifest dict"
```

**PowerShell Multi-line Commits:**
```powershell
# Use multiple -m flags (NOT multiline strings)
git commit -m "feat(testing): add pytest framework" `
           -m "" `
           -m "- Added pytest with coverage, mocking, asyncio plugins" `
           -m "- Created test fixtures and configuration" `
           -m "- Established 8% baseline coverage"
```

**Commit Best Practices:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor" not "Moves cursor")
- Limit first line to 72 characters
- Reference issues: `Fixes #123`, `Closes #456`
- Explain WHY in body, not just what changed

## Extending the System

### Adding a New Domain

1. Create a new directory in `domains/`
2. Implement domain processor and models
3. Register the domain with the system
4. Add domain-specific CLI commands

Example domain registration:

```python
from .. import DomainProcessor, register_domain

class MyDomainProcessor(DomainProcessor):
    """My custom domain processor."""
    # Implementation

# Register the domain
register_domain("my_domain", MyDomainProcessor)
```

### Adding a New Plugin

1. Create a new directory in `plugins/`
2. Create a `manifest.json` file
3. Implement link handlers
4. Register with appropriate domains

### Adding a New Link Type

1. Create a new handler class extending `LinkHandler`
2. Implement the `execute` and `get_schema` methods
3. Register the link type with `register_link_type`

Example link handler:

```python
from core.links import LinkHandler, register_link_type

class MyLinkHandler(LinkHandler):
    """Handler for my_link link type."""
    
    @classmethod
    def execute(cls, link_config, context):
        # Implementation
        return {"result": "success"}
    
    @classmethod
    def get_schema(cls):
        return {
            "type": "object",
            "properties": {
                # Properties definition
            }
        }

# Register the link type
register_link_type("my_link", MyLinkHandler)
```

### Creating a Package

Packages allow distributing extensions without modifying the core codebase:

1. Create a package template:
   ```bash
   python main.py packages create my_package --domain my_domain --plugin my_plugin
   ```

2. Develop your package components
3. Install for testing:
   ```bash
   pip install -e ./hottopoteto-my_package
   ```

See [Package Management](docs/packages.md) for more details on package development.

## Pull Request Process

**Before Submitting:**
1. [ ] All tests pass locally (`pytest`)
2. [ ] Code coverage meets requirements (`pytest --cov`)
3. [ ] Documentation updated (if applicable)
4. [ ] CHANGELOG.md updated (if applicable)
5. [ ] Conventional commit messages used
6. [ ] No merge conflicts with main branch

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Coverage: XX%

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

**After Submission:**
- Respond to review comments promptly
- Make requested changes in new commits (don't force-push)
- Request re-review after addressing feedback

### Review Process

- Maintainers will review your code
- They may request changes or improvements
- Once approved, your code will be merged

## Release Process

- Version numbers follow semantic versioning
- Release candidates are created before full releases
- Releases are published to PyPI and GitHub

## Questions?

If you have questions, please open an issue or contact the maintainers.

Thank you for contributing to Hottopoteto!