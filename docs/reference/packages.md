# Package Management Reference

This document provides a comprehensive reference for Hottopoteto's package management system.

## CLI Commands

### List Installed Packages

```bash
python main.py packages list
```

Lists all packages currently installed and registered with Hottopoteto.

### Install a Package

```bash
python main.py packages install <package-name>
```

Installs a package from PyPI, GitHub, or local directory.

Options:
- `--dev`: Install in development mode (equivalent to pip install -e)

Examples:
```bash
# Install from PyPI
python main.py packages install linguistics

# Install from GitHub
python main.py packages install git+https://github.com/username/hottopoteto-linguistics.git

# Install local package in development mode
python main.py packages install --dev ./hottopoteto-linguistics
```

### Uninstall a Package

```bash
python main.py packages uninstall <package-name>
```

Removes an installed package.

### Create a Package Template

```bash
python main.py packages create <name> [--domain <domain-name>] [--plugin <plugin-name>]
```

Creates a new package template with optional domain and plugin templates.

Examples:
```bash
# Basic package
python main.py packages create my_package

# Package with a domain
python main.py packages create my_package --domain my_domain

# Package with a domain and plugin
python main.py packages create my_package --domain my_domain --plugin my_plugin
```

## Package Registry API

### Registration

```python
from core.registry import PackageRegistry

# Register package
PackageRegistry.register_package("my_package", __name__)

# Register domain from package
PackageRegistry.register_domain_from_package(
    "my_package",  # Package name
    "my_domain",   # Domain name
    domain_module  # Domain module object
)

# Register plugin from package
PackageRegistry.register_plugin_from_package(
    "my_package",  # Package name
    "my_plugin",   # Plugin name
    plugin_module  # Plugin module object
)
```

### Querying

```python
# List all packages
packages = PackageRegistry.list_packages()

# Get a specific package
package = PackageRegistry.get_package("my_package")
```

## Entry Points

Hottopoteto discovers packages using the `hottopoteto.packages` entry point group:

```python
# setup.py
setup(
    name="hottopoteto-my_package",
    # ...
    entry_points={
        "hottopoteto.packages": [
            "my_package=hottopoteto_my_package:register",
        ],
    },
    # ...
)
```

## Package Discovery

On startup, Hottopoteto:

1. Scans for installed packages with the `hottopoteto.packages` entry point
2. Loads each package's `register` function
3. Executes the registration code
4. Updates the necessary registries (packages, domains, plugins)

This happens when the package is imported:

```python
# __init__.py
def discover_packages():
    for entry_point in pkg_resources.iter_entry_points("hottopoteto.packages"):
        register_func = entry_point.load()
        register_func()
```
