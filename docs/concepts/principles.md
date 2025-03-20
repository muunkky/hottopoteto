# Core Principles of Hottopoteto

This document outlines the fundamental design principles that guide Hottopoteto's architecture.

## 1. Domain Isolation

**Principle**: Links are limited to a single domain. Components used by a link must be in that domain.

**Rationale**: This ensures clean separation of concerns and prevents circular dependencies between domains.

**Implementation**: 
- Each link type belongs to a specific domain
- Links can only directly use models and functions from their own domain
- Domain-specific code is organized in domain directories

## 2. Cross-Domain Communication

**Principle**: Only core infrastructure can facilitate communication between domains.

**Rationale**: Direct domain-to-domain dependencies would create a tangled web of connections.

**Implementation**:
- Domains communicate via shared context in recipes
- Standard data formats enable interoperability
- Core utilities provide domain-agnostic functions

## 3. Output Constraints

**Principle**: Links can only write to their domain's output folder and the root output folder.

**Rationale**: Prevents links from interfering with other domains' data.

**Implementation**:
- Links write to `output/domain_name/`
- Common outputs go to `output/`
- Output paths are automatically created

## 4. Recipe Composition

**Principle**: Recipes orchestrate functionality across domains.

**Rationale**: Users need to combine capabilities from different domains without dealing with domain internals.

**Implementation**:
- Recipes reference links from any domain
- Common context passes data between links
- Recipes represent workflows, not individual functions

## 5. Template Referencing

**Principle**: Only recipe templates can reference other templates. Text templates are standalone.

**Rationale**: Prevents circular references and keeps the template system simple.

**Implementation**:
- Recipe templates can include or extend other recipes
- Text templates contain placeholders but no template references
- Template resolution follows a clear hierarchy

## 6. Sensitive Information

**Principle**: The system never stores sensitive information like API keys in code or configuration files.

**Rationale**: Security best practices require keeping credentials separate from code.

**Implementation**:
- Credentials are stored in `.env` files (not committed to version control)
- Hierarchical credential loading (domain-specific → core → root)
- Interactive credential management tools

## 7. Domain-Driven Organization

**Principle**: Code is organized primarily by domain, not by technical function.

**Rationale**: Domain-oriented architecture creates natural boundaries.

**Implementation**:
- Each domain has a standard structure
- Plugins can implement or extend domains
- Registries connect domains to the core infrastructure

## 8. Plugin Extensibility

**Principle**: The system should be extensible without modifying core code.

**Rationale**: A plugin architecture allows flexible extension without breaking upgrades.

**Implementation**:
- Clear extension points for plugins
- Automatic discovery of plugins
- Standard interfaces for integration
