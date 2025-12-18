# [ADR-0002] Domain Registration System

## Status

Accepted

## Context

For Hottopoteto to support diverse domains like language processing, data storage, and others, we needed a flexible system to register, discover, and use domain-specific functionality. Key requirements included:

- Ability to dynamically discover available domains
- Register domain interfaces, schemas, and functions
- Associate packages with domains
- Retrieve domain-specific functionality at runtime
- Support for versioning domain interfaces

## Decision

We have implemented a Domain Registration System with the following components:

1. **Domain Registry**: A central registry that stores all registered domains, schemas, and functions
2. **Registration Functions**:
   - `register_domain_interface`: Register a new domain interface
   - `register_package_for_domain`: Associate a package with a domain
   - `register_domain_schema`: Register a schema for a domain
   - `register_domain_function`: Register a function for a domain

3. **Discovery Functions**:
   - `list_domains`: Return a list of all registered domains
   - `get_domain_interface`: Get the interface for a specific domain
   - `get_packages_for_domain`: Get packages associated with a domain
   - `get_domain_function`: Get a function registered for a domain

The implementation is primarily in `core/registration/domains.py`, with compatibility imports in `core/domains/__init__.py` and `core/domains.py`.

## Consequences

### Positive Consequences

- Domains can be dynamically discovered and used at runtime
- Package developers can easily register domain-specific functionality
- Clear API for registering and accessing domain components
- Support for multiple versions of domain interfaces
- Separation between domain definition and implementation

### Negative Consequences

- Increased complexity compared to direct imports
- Potential for registration conflicts if not managed properly
- Runtime errors if domains or functions are missing
- Need to maintain backward compatibility in the registration system

## Alternatives Considered

**Direct Import System**: Having domains directly import functionality from other domains. Rejected due to tight coupling and inability to support dynamic discovery.

**Service Locator Pattern**: Using a service locator to find domain implementations. Partially incorporated into the registry system, but with more structured registration.

**Dependency Injection**: Having a container inject domain dependencies. Considered too complex for the primary use cases.

## Related Documents

- [Code Structure Technical Reference](../../reference/architecture-map.md)
- [Domain Management Functions](../../reference/architecture-map.md#domain-management-functions)
