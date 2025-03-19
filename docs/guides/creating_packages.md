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

## Domain vs Plugin vs Package

Understanding these concepts is crucial:

- **Package**: A distributable Python module with its own installation and configuration
- **Domain**: A knowledge area with specific data models and functions (e.g., linguistics, storage)
- **Plugin**: A component that adds new link types or other capabilities (e.g., MongoDB connector)

A package can contain:
- Zero, one, or multiple domains
- Zero, one, or multiple plugins
- Shared utilities and schemas

### Example: Analytics Package

```
hottopoteto-analytics/
├── hottopoteto_analytics/
│   ├── __init__.py               # Package registration
│   ├── domains/
│   │   ├── __init__.py
│   │   └── metrics/              # Metrics domain
│   │       ├── __init__.py       # Domain registration
│   │       ├── models.py         # Metrics data models
│   │       └── functions.py      # Metrics calculation functions
│   └── plugins/
│       ├── __init__.py
│       ├── prometheus/           # Prometheus plugin
│       │   ├── __init__.py       # Plugin registration
│       │   └── links.py          # prometheus.export link
│       └── grafana/              # Grafana plugin
│           ├── __init__.py       # Plugin registration
│           └── links.py          # grafana.dashboard link
├── setup.py                      # Package metadata
└── README.md                     # Documentation
```

This example package:
- Implements the `metrics` domain
- Provides two plugins: `prometheus` and `grafana`
- Each plugin registers its own link types

## Registration Process Flow

When your package is loaded, registration typically follows this order:

1. Package registers itself
```python
def register():
    PackageRegistry.register_package("analytics", __name__)
    # Import submodules to trigger their registration
    from . import domains, plugins
    return True
```

2. Domains register with both domain system and package
```python
# domains/metrics/__init__.py
register_domain_interface("metrics", {...})
PackageRegistry.register_domain_from_package("analytics", "metrics", __name__)
```

3. Plugins register with the package
```python
# plugins/prometheus/__init__.py
PackageRegistry.register_plugin_from_package("analytics", "prometheus", __name__)
```

4. Links register with the link system
```python
# plugins/prometheus/links.py
register_link_type("prometheus.export", PrometheusExportLink)
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
