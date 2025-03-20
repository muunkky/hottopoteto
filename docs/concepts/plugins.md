# Plugin System in Hottopoteto

The plugin system enables extending the framework with new capabilities.

## What Are Plugins?

Plugins are components that extend Hottopoteto with new:

- Link types
- Storage adapters
- Utilities
- Domain implementations

Each plugin integrates with the core system through standardized interfaces, allowing for a modular and extensible architecture.

## Plugin Architecture

Plugins are organized as packages with a specific structure:

```
plugins/my_plugin/               # Plugin root directory
├── __init__.py                  # Plugin initialization
├── links.py                     # Link handlers
├── manifest.json                # Plugin metadata
├── requirements.txt             # Dependencies
└── schemas/                     # JSON schemas
    └── link_schema.py           # Schema definitions
```

### Plugin Manifest

Each plugin includes a `manifest.json` file that defines its metadata:

```json
{
  "name": "gemini",
  "version": "1.0.0",
  "description": "Google Gemini API integration",
  "requirements": ["google-generativeai>=0.3.0"],
  "entry_points": {
    "link_handlers": ["links.py"]
  },
  "domains": [
    {
      "name": "llm",
      "version": "1.0.0"
    }
  ]
}
```

## Plugin Types

### Link Type Plugins

Link type plugins add new link types that can be used in recipes:

```python
class MyLinkHandler(LinkHandler):
    """Handler for my_link link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute this link type."""
        # Implementation
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for this link type's configuration."""
        return {
            # Schema definition
        }

# Register the link type
register_link_type("my_link", MyLinkHandler)
```

### Storage Adapter Plugins

Storage adapter plugins add new storage backends:

```python
class MyStorageAdapter(StorageAdapter):
    """Custom storage adapter."""
    
    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'MyStorageAdapter':
        """Initialize with configuration."""
        # Implementation
    
    # Implement required methods

# Register the adapter
register_adapter("my_storage", MyStorageAdapter)
```

### Domain Implementation Plugins

Plugins can implement domain interfaces:

```python
# Register handlers for domain-specific operations
register_domain_function("my_domain", "process_data", process_data_function)
```

## Using Plugins

### Listing Available Plugins

```bash
python main.py plugins list
```

### Getting Plugin Information

```bash
python main.py plugins info gemini
```

### Using Plugin Links in Recipes

```yaml
name: "Plugin Example"
links:
  - name: "Plugin_Link"
    type: "my_link"
    operation: "custom_operation"
    data:
      param1: "value1"
      param2: "value2"
```

## Plugin Discovery and Loading

The system discovers and loads plugins by:

1. Discovery: Scanning the plugins directory
2. Manifest Loading: Reading each plugin's manifest.json
3. Module Loading: Importing plugin modules
4. Registration: Registering link types and other extensions

## Plugin-Domain Integration

Plugins can support specific domains by registering with them:

```python
# Register package for domain
register_package_for_domain("llm", "gemini")
```

This creates a mapping between domains and the packages that support them.

## Core vs. Plugin Functionality

The core system provides:

- Basic link types (llm, user_input, function)
- Core schema registry
- Recipe execution engine
- Domain system

Plugins extend this with:

- Specialized link types
- External service integrations
- Custom storage adapters
- Domain implementations

For detailed instructions on creating plugins, see the [Creating Plugins](../guides/creating-plugins.md) guide.
