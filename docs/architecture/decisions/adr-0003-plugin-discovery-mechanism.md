# [ADR-0003] Plugin Discovery Mechanism

## Status

Accepted

## Context

Hottopoteto needs to be extensible through plugins that can add new link types, domain functionality, and other capabilities. We needed a mechanism to:

- Discover plugins automatically
- Load plugin functionality at runtime
- Allow plugins to register their components
- Handle plugin dependencies
- Support plugin versioning

## Decision

We have decided to implement a Plugin Discovery Mechanism based on Python entry points and a plugin registry:

1. **Entry Point Discovery**: Plugins declare themselves using Python entry points in their setup.py or pyproject.toml files.

2. **Plugin Registry**: A central registry that maintains information about discovered plugins, their link types, and domain extensions.

3. **Self-Registration**: Plugins use the registration API to register their components (links, domains, schemas) when loaded.

4. **Lazy Loading**: Plugins are discovered on startup but their code is only loaded when needed.

The implementation spans:
- `plugins/loader.py`: Discovers plugins from entry points
- `plugins/registry.py`: Maintains the plugin registry
- Integration with the domain registration system

## Consequences

### Positive Consequences

- Plugins can be distributed as standard Python packages
- New functionality can be added without modifying the core code
- Users can install only the plugins they need
- Clear extension mechanism for third-party developers
- Support for versioned plugins

### Negative Consequences

- Complexity in managing plugin interactions
- Potential for conflicts between plugins
- Performance impact from dynamic discovery and loading
- Need to maintain compatibility across plugin versions

## Alternatives Considered

**Directory-Based Discovery**: Scanning directories for plugins. Rejected in favor of the more standardized entry point mechanism.

**Manual Plugin Registration**: Requiring users to explicitly register plugins. Rejected for being less user-friendly.

**Import Hook System**: Using Python import hooks for plugin discovery. Rejected as overly complex for our needs.

## Related Documents

- [Plugin System Architecture](../../reference/architecture-map.md#plugin-system-architecture)
- [Architecture Overview](../../concepts/architecture.md#plugins)
