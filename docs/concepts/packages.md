# Package System in Hottopoteto

This document provides a comprehensive overview of Hottopoteto's package system.

## What Are Packages?

Packages are Python modules that extend Hottopoteto with new domains, plugins, and other components. They can be installed with pip and discovered automatically by Hottopoteto.

## Package Architecture

### Core vs Extension Packages

Hottopoteto uses a modular architecture with two main types of packages:

#### 1. Core Package

The **Core Package** provides:

- Base classes and interfaces
- Registry systems
- Core link types (LLM, function, user_input)
- Core utilities
- Package discovery and loading system

The core package is always present and serves as the foundation for all extensions. It's the "native" functionality that all other components can rely on.

#### 2. Extension Packages

**Extension Packages** add new capabilities:

- New domains (like linguistics, storytelling, etc.)
- New plugins (like database connectors, API integrations)
- New link types
- New utilities

Extension packages are discovered dynamically using Python's entry point system and can be installed or removed without modifying the core code.

## Package Structure

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

## Package Loading Sequence

When Hottopoteto starts:

1. The core package initializes first
2. The core registers its built-in components
3. Extension packages are discovered via entry points
4. Each extension registers its components with the appropriate registries
5. All components are available for use in recipes

## Dependency Management

The dependency relationship is unidirectional:

- Extensions can depend on core components
- Core components should NEVER depend on extensions
- Extensions can optionally depend on other extensions

This ensures a clean separation and prevents circular dependencies.

## Package Management

### CLI Commands

#### List Installed Packages

```bash
python main.py packages list
```

#### Install a Package

```bash
python main.py packages install <package-name>
```

Options:
- `--dev`: Install in development mode (equivalent to pip install -e)

#### Uninstall a Package

```bash
python main.py packages uninstall <package-name>
```

#### Create a Package Template

```bash
python main.py packages create <name> [--domain <domain-name>] [--plugin <plugin-name>]
```

### Package Discovery

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

On startup, Hottopoteto:

1. Scans for installed packages with the `hottopoteto.packages` entry point
2. Loads each package's `register` function
3. Executes the registration code
4. Updates the necessary registries (packages, domains, plugins)

## Best Practices

When deciding whether functionality should be in the core (native) or an extension package:

### Should be in Core:

- Framework infrastructure
- Core abstractions and interfaces
- Common utilities needed by most extensions
- Default implementations of essential systems
- Package management system itself

### Should be in Extensions:

- Domain-specific knowledge and models
- Integration with external services
- Specialized algorithms
- Optional features
- Experimental functionality

For detailed instructions on creating packages, see the [Creating Packages Guide](../guides/creating-packages.md).
