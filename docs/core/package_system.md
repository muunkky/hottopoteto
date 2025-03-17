# Hottopoteto Package System

This document explains the philosophy and architecture of the Hottopoteto package system, including the distinction between core functionality and installable packages.

## Core vs Extension Packages

Hottopoteto uses a modular architecture with two main types of packages:

### 1. Core Package

The **Core Package** is the central framework that provides:

- Base classes and interfaces
- Registry systems
- Core link types (LLM, function, user_input)
- Core utilities
- Package discovery and loading system

The core package is always present and serves as the foundation for all extensions. It's the "native" functionality that all other components can rely on.

### 2. Extension Packages

**Extension Packages** are installable modules that add new capabilities:

- New domains (like linguistics, storytelling, etc.)
- New plugins (like database connectors, API integrations)
- New link types
- New utilities

Extension packages are discovered dynamically using Python's entry point system and can be installed or removed without modifying the core code.

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

## Core Package Components

The core package includes:

- **Registry System**: Central registration for components
- **Domain System**: Base classes for domain implementation
- **Plugin System**: Framework for plugin discovery
- **Link System**: Core link types and interfaces
- **Schema System**: Schema validation and utilities
- **Storage System**: Base storage interfaces
- **CLI System**: Command-line interface framework

## Extension Package Components

Extension packages can provide:

- **Domain Implementations**: New specialized domains
- **Plugin Implementations**: New plugins for external services
- **Link Types**: New types of operations for recipes
- **Schemas**: New schema definitions
- **Utilities**: Helper functions and tools
- **CLI Commands**: Custom commands for the CLI

## Native vs Installed Functionality

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

## Best Practices

1. **Minimize Core Dependencies**: The core should have minimal external dependencies
2. **Clean Interfaces**: Define clear interfaces between core and extensions
3. **Feature Isolation**: Keep features self-contained within their packages
4. **Version Compatibility**: Maintain backward compatibility in core APIs
5. **Documentation**: Document all extension points and interfaces
