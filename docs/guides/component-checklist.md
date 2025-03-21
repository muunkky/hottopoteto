# New Component Checklist

This checklist helps ensure that new components follow Hottopoteto's architectural principles and best practices.

## Domain Components

When creating a new domain component:

- [ ] **Registration**: Domain is properly registered using `register_domain_interface`
- [ ] **Directory Structure**: Component follows standard domain directory structure
  - [ ] Located in `core/domains/{domain_name}/` or in a package's `domains/{domain_name}/`
  - [ ] Has `__init__.py` that handles registration
  - [ ] Implements required domain files (models.py, links.py, etc.)
- [ ] **Interface Definition**: Domain interface has all required fields
  - [ ] Name and version are defined
  - [ ] Schemas or functions are properly specified
- [ ] **Isolation**: Domain doesn't import from or depend on plugins
- [ ] **Documentation**: Domain has appropriate documentation
  - [ ] README.md describes the domain's purpose and components
  - [ ] Function and schema documentation included
- [ ] **Testing**: Domain has proper tests
  - [ ] Unit tests for domain functions
  - [ ] Schema validation tests

## Plugin Components

When creating a new plugin:

- [ ] **Configuration**: Contains plugin.yaml or plugin.json with required metadata
- [ ] **Structure**: Plugin follows standard directory structure
  - [ ] Located in `plugins/{plugin_name}/` 
  - [ ] Has `__init__.py` that handles registration
  - [ ] Organizes link handlers in `links/`
- [ ] **Registration**: Properly registers with the plugin system
  - [ ] Link types follow `{plugin_name}.{operation}` convention
  - [ ] Links are registered using `register_link_type`
- [ ] **Error Handling**: Implements proper error handling and validation
- [ ] **Documentation**: Plugin has appropriate documentation
  - [ ] README.md describes functionality and configuration
  - [ ] Link type documentation with examples
- [ ] **Testing**: Plugin has proper tests
  - [ ] Unit tests for link handlers
  - [ ] Integration test recipes

## Link Type Components

When creating a new link type:

- [ ] **Domain Association**: Link type belongs to a specific domain
- [ ] **Naming**: Link type follows naming convention
  - [ ] Core links: simple name (e.g., "llm")
  - [ ] Plugin links: `{plugin_name}.{operation}`
- [ ] **Schema Definition**: Input and output schemas properly defined
- [ ] **Execution**: Implements `execute` method to handle link execution
- [ ] **Output Format**: Returns properly structured output data
- [ ] **Context**: Correctly interacts with execution context
- [ ] **Documentation**: Includes documentation for parameters and behavior
- [ ] **Testing**: Has dedicated tests for functionality

## Package Components

When creating a new package:

- [ ] **Structure**: Follows package directory structure conventions
  - [ ] Root directory uses hyphenated name (`hottopoteto-my_package`)
  - [ ] Python module uses underscore name (`hottopoteto_my_package`)
- [ ] **Registration**: Package properly registers its components
- [ ] **Dependencies**: Dependencies correctly specified in setup.py
- [ ] **Documentation**: Package has comprehensive documentation
  - [ ] README.md with usage instructions
  - [ ] Examples of using the package components
- [ ] **Testing**: Package has adequate test coverage
  - [ ] Tests for all main components
  - [ ] Integration tests that verify registration

## Architecture Compliance

All new components should comply with these architectural principles:

- [ ] **Domain Isolation**: Components respect domain boundaries
- [ ] **Cross-Domain Communication**: Only through core infrastructure
- [ ] **Output Constraints**: Links write only to domain or root output folders
- [ ] **Security**: No credentials in code
- [ ] **Organization**: Code organized by domain, not technical function
- [ ] **Extensibility**: Designed for extension without core modifications
- [ ] **Domain Dependencies**: Domains don't depend on plugins
- [ ] **Template Hierarchy**: Template references follow the established rules

## Related Documentation

- [Architecture Principles](../reference/architecture-principles-summary.md)
- [Creating Domains](creating-domains.md)
- [Creating Plugins](creating_plugins.md)
- [Creating Packages](creating-packages.md)
- [Architecture Decisions](../architecture/decisions/)