# Package Management

Hottopoteto supports a flexible package system that allows you to extend the framework with new domains, plugins, and other components.

## Package Types

Hottopoteto uses two types of packages:

1. **Core Package**: The built-in framework functionality that all other packages depend on
2. **Extension Packages**: Additional packages that add new capabilities

See [Package System Architecture](docs/core/package_system.md) for more details on this distinction.

## Package Structure

A standard Hottopoteto extension package follows this structure:

```
hottopoteto-<name>/                # Distribution package (hyphenated)
├── README.md                      # Package documentation
├── LICENSE                        # License file
├── setup.py                       # Package metadata and entry points
└── hottopoteto_<name>/            # Python module (underscored)
    ├── __init__.py                # Package registration
    ├── components/                # Shared components
    │   └── __init__.py
    ├── domains/                   # Domain implementations
    │   └── example_domain/
    │       ├── __init__.py
    │       ├── models.py
    │       └── schema.py
    └── plugins/                   # Plugin implementations
        └── example_plugin/
            ├── __init__.py
            ├── links.py
            └── schemas/
```

## Managing Packages

### Creating a Package

Use the built-in package template generator:

```bash
python main.py packages create my_package --domain example --plugin demo
```

This creates a template with the specified domain and plugin.

### Installing Packages

Install from PyPI:

```bash
python main.py packages install linguistics
```

Install from GitHub:

```bash
python main.py packages install git+https://github.com/username/hottopoteto-linguistics.git
```

Install a local package (for development):

```bash
python main.py packages install --dev ./hottopoteto-linguistics
```

### Listing Installed Packages

```bash
python main.py packages list
```

### Uninstalling Packages

```bash
python main.py packages uninstall linguistics
```

## Developing a Package

See the [Creating Packages](docs/guides/creating_packages.md) guide for detailed instructions on package development.

## Package Discovery

When Hottopoteto starts, it:

1. Registers the core package
2. Discovers and loads extension packages via entry points
3. Initializes components from all packages

This happens automatically when the framework is imported.

## For More Information

- [Package System Architecture](docs/core/package_system.md): Details on core vs extension packages
- [Creating Packages](docs/guides/creating_packages.md): Guide to creating new packages
- [Package Reference](docs/reference/packages.md): Reference for CLI commands and API
