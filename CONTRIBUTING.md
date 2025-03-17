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
2. Clone your fork: `git clone https://github.com/muunkky/hottopoteto.git`
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

# Install development dependencies
pip install -r requirements-dev.txt
```

## Project Structure

```
hottopoteto/
├── core/                  # Core system components
├── domains/               # Domain implementations
├── plugins/               # Plugin implementations
├── recipes/               # Recipe definitions
└── storage/               # Storage system
```

## Contribution Guidelines

### Code Style

- Follow the PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep lines under 100 characters

### Documentation

- Update documentation when changing code
- Add examples for new features
- Use Markdown for documentation files

### Testing

- Write tests for new features
- Ensure existing tests pass
- Use pytest for testing

Example test:

```python
def test_function():
    result = function_to_test(input_value)
    assert result == expected_value
```

### Commit Messages

Write clear commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor" not "Moves cursor")
- Limit the first line to 72 characters
- Reference issues and pull requests

Example:

```
Add word derivation utility for conlang domain

- Implements derivation rules based on phonological patterns
- Adds tests for derivation functionality
- Updates documentation

Fixes #123
```


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

## Pull Request Process

- Update documentation if necessary
- Add or update tests
- Ensure all tests pass
- Update the `CHANGELOG.md` file if applicable
- Submit the pull request

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