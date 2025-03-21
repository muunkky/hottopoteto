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

See our [Architecture Principles](docs/reference/architecture-principles-summary.md) document and [Component Checklist](docs/guides/component-checklist.md) for detailed guidance.

## Architecture Validation

We use automated architecture tests to ensure contributions maintain the system's architectural integrity:

```bash
# Run architecture validation tests
pytest -m architecture
```
These tests verify that components follow our domain registration patterns and directory structures.


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
│   ├── domains/           # Domain implementations
│   ├── links/             # Link system
│   ├── registration/      # Registration system
│   └── schemas/           # Schema definitions
├── plugins/               # Plugin implementations 
├── docs/                  # Documentation
│   ├── concepts/          # Core concepts
│   ├── guides/            # How-to guides
│   └── reference/         # Technical reference
├── tests/                 # Test suite
│   └── architecture/      # Architecture validation tests
└── recipes/               # Recipe definitions
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