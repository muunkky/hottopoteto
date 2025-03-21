# Code Structure Technical Reference

This document provides a detailed technical reference of Hottopoteto's code organization and implementation details, serving as a developer companion to the [high-level architecture overview](../concepts/architecture.md).

## System Implementation Map

The following diagram shows how the conceptual architecture is implemented across files and modules:

```mermaid
graph TD
    classDef core fill:#FF66B2,stroke:#333,stroke-width:2px,color:#000
    classDef domains fill:#6699FF,stroke:#333,stroke-width:1px,color:#000
    classDef plugins fill:#66CC66,stroke:#333,stroke-width:1px,color:#000
    classDef cli fill:#FF6666,stroke:#333,stroke-width:1px,color:#000

    
    main[main.py]:::cli
    
    %% Core Components
    executor[core.executor]:::core
    links[core.links]:::core
    domains[core.domains]:::domains
    registration[core.registration.domains]:::domains
    schemas[core.schemas]:::core
    
    %% CLI Components
    cli_packages[core.cli.commands.packages]:::cli
    cli_credentials[core.cli.commands.credentials]:::cli
    cli_recipes[core.cli.commands.recipes]:::cli
    
    %% Plugin System
    plugins[plugins.*]:::plugins
    
    %% Relationships
    main --> executor
    main --> cli_packages
    main --> cli_credentials
    main --> cli_recipes
    main --> domains
    
    executor --> links
    executor --> domains
    links --> plugins
    domains --> registration
    
    %% Legend
    subgraph Legend
        core_legend[Core System]:::core
        domains_legend[Domains]:::domains
        plugins_legend[Plugins]:::plugins
        cli_legend[CLI]:::cli
    end
```

## Module Dependency Graph

```mermaid
flowchart TD
    subgraph EntryPoint
        main[main.py]
    end
    
    subgraph CoreSystem
        executor[core.executor]
        links[core.links]
        schemas[core.schemas]
    end
    
    subgraph DomainSystem
        domains[core.domains]
        registration[core.registration.domains]
        domain_interfaces[domains.*]
    end
    
    subgraph CLI
        cli_commands[core.cli.commands]
        cli_packages[core.cli.commands.packages]
        cli_credentials[core.cli.commands.credentials]
        cli_recipes[core.cli.commands.recipes]
    end
    
    subgraph PluginSystem
        plugin_loader[plugins.loader]
        plugin_registry[plugins.registry]
        plugins[plugins.*]
    end
    
    %% Connections
    main --> executor
    main --> cli_commands
    cli_commands --> cli_packages
    cli_commands --> cli_credentials
    cli_commands --> cli_recipes
    
    executor --> links
    executor --> domains
    
    domains --> registration
    domains --> domain_interfaces
    
    links --> plugin_registry
    plugin_registry --> plugins
    plugin_loader --> plugins
```

## Component Details

### Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI Interface
    participant Executor as RecipeExecutor
    participant Links as Link System
    participant Domains as Domain System
    participant Storage as Storage System
    
    User->>CLI: Run recipe command
    CLI->>Executor: Load and execute recipe
    
    loop For each link in recipe
        Executor->>Links: Execute link
        Links->>Domains: Use domain functions (if needed)
        Links->>Storage: Store data (if needed)
        Links-->>Executor: Return link result
    end
    
    Executor-->>CLI: Return final result
    CLI-->>User: Display output
```

### main.py
Entry point containing:
- `core.executor.RecipeExecutor`
- CLI command handlers for packages and credentials
- Domain management functionality

### core.cli.commands.packages
Package management commands:
- `packages_group`
- `list_packages`
- `install_package`
- `uninstall_package`
- `create_package`

### core.cli.commands.credentials
Credential management commands:
- `add_credentials_command`
- `handle_credentials_command`

### Domain Management System

```mermaid
classDiagram
    class DomainRegistry {
        +domains: Dict
        +schemas: Dict
        +functions: Dict
        +list_domains()
        +get_domain_interface()
        +register_domain_interface()
        +register_domain_schema()
        +register_domain_function()
        +get_domain_function()
    }
    
    class DomainInterface {
        +name: str
        +version: str
        +schemas: Dict
        +functions: Dict
        +get_schema()
        +call_function()
    }
    
    class PackageRegistry {
        +domain_packages: Dict
        +register_package_for_domain()
        +get_packages_for_domain()
    }
    
    DomainRegistry --> DomainInterface : manages
    DomainRegistry --> PackageRegistry : uses
```

The domain management functionality is implemented across several files:

```mermaid
graph TD
    core_domains_init[core/domains/__init__.py<br/>Imports from registration]
    core_domains_py[core/domains.py<br/>Legacy file]
    core_registration[core/registration/domains.py<br/>Main implementation]
    
    core_domains_init --> core_registration
    core_domains_py --> core_registration
    
    subgraph "Implementation Details"
        core_registration --> domain_registry[DomainRegistry]
        core_registration --> domain_interface[DomainInterface]
        core_registration --> package_registry[PackageRegistry]
    end
```

#### Domain Management Functions

The following functions are available for domain management:

| Function | Description |
|----------|-------------|
| `list_domains` | Returns a list of all registered domains |
| `get_domain_interface` | Retrieves interface for a specific domain |
| `get_packages_for_domain` | Lists packages registered for a domain |
| `register_domain_interface` | Registers a new domain interface |
| `register_package_for_domain` | Associates a package with a domain |
| `register_domain_schema` | Registers a schema for a domain |
| `register_domain_function` | Registers a function for a domain |
| `get_domain_function` | Retrieves a function registered for a domain |

## Plugin System Architecture

```mermaid
graph TD
    subgraph "Plugin Discovery"
        entry_points[Entry Points] --> plugin_loader
        plugin_loader[Plugin Loader] --> plugin_registry
    end
    
    subgraph "Plugin Registry"
        plugin_registry[Plugin Registry]
        plugin_registry --> link_types[Link Types]
        plugin_registry --> domain_extensions[Domain Extensions]
    end
    
    subgraph "Plugin Usage"
        executor[RecipeExecutor] --> plugin_registry
        domains[Domain System] --> plugin_registry
    end
```

## File Structure

- **main.py**: Project entry point
- **core/domains/__init__.py**: Domain system entry point, imports from registration
- **core/domains.py**: Legacy file that redirects to registration (consider deprecating)
- **core/registration/domains.py**: Core implementation of domain management system

## Relationship to Architecture Concepts

This section maps the code modules to the architectural concepts described in the [architecture overview](../concepts/architecture.md):

| Architecture Concept | Implementation Modules |
|----------------------|------------------------|
| Recipes | Defined as YAML files, loaded by `core.executor` |
| Executor | `core.executor.RecipeExecutor` |
| Links | `core.links.*` |
| Domains | `core.domains` and `core.registration.domains` |
| Plugins | Discovered and loaded via package system |

## Using This Reference

This document is intended for:
- Developers extending the system
- Contributors to the core codebase
- Users creating custom packages or plugins

For high-level understanding, please refer to the [architecture overview](../concepts/architecture.md).