# [ADR-0001] Domain Isolation Pattern

## Status

Accepted

## Context

In building Hottopoteto, we needed a system architecture that would allow different specialized knowledge domains to coexist without tight coupling, while still enabling them to work together through recipes. This led to questions about how to organize domain-specific code, schemas, and functions in a way that promotes modularity and extensibility.

Key considerations:
- How to allow domains to define their own data models
- How to prevent cross-domain dependencies
- How to enable recipe execution across different domains
- How to facilitate discovery and registration of domains

## Decision

We have decided to adopt a Domain Isolation Pattern, where each domain:

1. Is implemented as a separate module with clear boundaries
2. Registers its own schemas and functions with a central registry
3. Can be packaged and distributed independently
4. Can be used by recipes without requiring other domains

The isolation is enforced through:
- A domain registry that serves as the central point of access for domain functionality
- Schema validation that ensures data conforms to domain-specific models
- Links as the primary mechanism for domain interaction
- A package system that enables independent installation of domains

## Consequences

### Positive Consequences

- Domains can be developed, tested, and deployed independently
- New domains can be added without modifying existing code
- Recipes can combine functionality from multiple domains
- Domain-specific schemas provide clear contracts for data exchange
- Package management system simplifies distribution and installation

### Negative Consequences

- Additional complexity in the domain registration system
- Potential performance overhead from schema validation between domains
- Learning curve for developers to understand domain boundaries
- Requires careful management of domain interfaces

## Alternatives Considered

**Monolithic Approach**: Having all domain functionality in a single codebase without clear boundaries. Rejected due to poor maintainability and scalability.

**Service-Oriented Approach**: Implementing domains as separate microservices. Rejected due to the complexity of managing service communication and deployment for a tool intended to run locally.

**Class Inheritance Hierarchy**: Using a class hierarchy to represent domain relationships. Rejected in favor of a more flexible registry-based approach that doesn't impose rigid hierarchies.

## Related Documents

- [Architecture Overview](../../concepts/architecture.md)
- [Code Structure Technical Reference](../../reference/architecture-map.md)
