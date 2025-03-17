# Creating Packages for Hottopoteto

This guide walks you through creating and distributing packages for Hottopoteto.

## What are Packages?

Packages are Python modules that extend Hottopoteto with new domains, plugins, schemas, and other components. They can be installed with pip and discovered automatically by Hottopoteto.

## Creating a Package

### Using the CLI Tool

The easiest way to create a new package is using the built-in package template generator:

```bash
python main.py packages create my_package --domain my_domain --plugin my_plugin
```

This creates a basic package structure with:
- A Python package named `hottopoteto_my_package`
- Registration code for the package
- Templates for the specified domain and plugin

### Package Structure

A standard package includes:

```
hottopoteto-my_package/           # Root directory (hyphenated)
├── README.md                     # Package documentation
└── hottopoteto_my_package/       # Python package (underscore)
    ├── __init__.py               # Registration code
    ├── components/               # Shared components
    │   └── __init__.py
    ├── domains/                  # Domain implementations
    │   └── my_domain/
    │       ├── __init__.py
    │       └── models.py
    ├── plugins/                  # Plugin implementations
    │   └── my_plugin/
    │       ├── __init__.py
    │       └── links.py
    └── setup.py                  # Package metadata
```

## Developing Your Package

### Package Registration

The package registers itself using the `PackageRegistry`:

```python
# __init__.py
def register():
    from core.registry import PackageRegistry
    PackageRegistry.register_package("my_package", __name__)
```

### Adding Domains

Domains are registered with both the package registry and domain system:

```python
# domains/my_domain/__init__.py
from core.registry import PackageRegistry
from core.domains import register_domain_interface

register_domain_interface("my_domain", {
    "name": "my_domain",
    "version": "0.1.0",
    "description": "My custom domain"
})

PackageRegistry.register_domain_from_package(
    "my_package", 
    "my_domain", 
    __name__
)
```

### Adding Plugins

Plugins are registered with the package registry:

```python
# plugins/my_plugin/__init__.py
from core.registry import PackageRegistry

PackageRegistry.register_plugin_from_package(
    "my_package",
    "my_plugin",
    __name__
)
```

### Testing During Development

Install your package in development mode:

```bash
cd hottopoteto-my_package
pip install -e .
```

## Distributing Your Package

### Publishing to PyPI

1. Prepare your package:
   ```bash
   python -m pip install --upgrade build twine
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

### Installation by Users

Users can install your package with:

```bash
python main.py packages install my_package
```

Or directly with pip:

```bash
pip install hottopoteto-my_package
```

## Best Practices

1. **Naming Conventions**:
   - Package name: `hottopoteto-my_package` (hyphenated)
   - Python module: `hottopoteto_my_package` (underscore)
   - Entry point: `my_package` (no prefix)

2. **Dependencies**:
   - Specify `hottopoteto` as a dependency in setup.py
   - Include all other dependencies your package needs

3. **Documentation**:
   - Include a detailed README.md
   - Document all domains, plugins and other components
   - Provide example recipes

4. **Testing**:
   - Add tests for your package components
   - Verify registration works correctly
   - Test with the Hottopoteto CLI

5. **Versioning**:
   - Use semantic versioning (MAJOR.MINOR.PATCH)
   - Update version in setup.py when releasing
