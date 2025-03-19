# Plugin System in Hottopoteto

The plugin system in Hottopoteto enables extending the framework with new capabilities. This document explains how the plugin system works and how to use it.

## What Are Plugins?

Plugins are components that extend Hottopoteto with new:

- Link types
- Storage adapters
- Utilities
- Domain implementations

Each plugin integrates with the core system through standardized interfaces, allowing for a modular and extensible architecture.

## Plugin Architecture

Plugins are organized as packages with a specific structure:

plugins/my_plugin/ ├── init.py # Plugin initialization ├── links.py # Link handlers ├── manifest.json # Plugin metadata ├── requirements.txt # Dependencies └── schemas/ # JSON schemas └── link_schema.py # Schema definitions


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

Plugin Registration
Plugins are automatically discovered and loaded when the system starts:

```python
def load_all_plugins() -> Dict[str, Dict[str, Any]]:
    """
    Discover and load all available plugins.
    """
    plugins = discover_plugins()
    for plugin_name in plugins:
        load_plugin(plugin_name)
    return _loaded_plugins
```

Plugin Types
Link Type Plugins
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

Storage Adapter Plugins
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

Domain Implementation Plugins
Plugins can implement domain interfaces:

# Register handlers for domain-specific operations
register_domain_function("my_domain", "process_data", process_data_function)

Using Plugins
Listing Available Plugins

python main.py plugins list

Getting Plugin Information

python main.py plugins info gemini

Using Plugin Links in Recipes

name: "Plugin Example"
links:
  - name: "Plugin_Link"
    type: "my_link"
    operation: "custom_operation"
    data:
      param1: "value1"
      param2: "value2"

Plugin Discovery and Loading
The system discovers and loads plugins by:

Discovery: Scanning the plugins directory
Manifest Loading: Reading each plugin's manifest.json
Module Loading: Importing plugin modules
Registration: Registering link types and other extensions

Plugin Dependencies
Plugins can specify dependencies in their requirements.txt file:
google-generativeai>=0.3.0
requests>=2.28.0
These dependencies should be installed for the plugin to work correctly.

Plugin-Domain Integration
Plugins can support specific domains by registering with them:
# Register package for domain
register_package_for_domain("llm", "gemini")
This creates a mapping between domains and the packages that support them.

Plugin Configuration
Plugins can be configured through environment variables or configuration files:

def load_plugin_config(plugin_name):
    """Load plugin configuration."""
    # Try environment variables first
    config = {}
    env_prefix = f"LANGCHAIN_{plugin_name.upper()}_"
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            config[key[len(env_prefix):].lower()] = value
            
    # Then try configuration file
    config_file = os.path.join("config", f"{plugin_name}.json")
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            file_config = json.load(f)
            config.update(file_config)
            
    return config



Core vs. Plugin Functionality
The core system provides:

Basic link types (llm, user_input, function)
Core schema registry
Recipe execution engine
Domain system
Plugins extend this with:

Specialized link types
External service integrations
Custom storage adapters
Domain implementations
Creating Plugins
For detailed instructions on creating plugins, see the Creating Plugins guide.

Troubleshooting Plugins
Common issues:

Missing dependencies
Incorrect manifest structure
Registration errors
To troubleshoot:

Check plugin requirements are installed
Verify manifest.json is valid
Check for error messages during plugin loading
Look for registration issues
Use the --debug flag for verbose logging:

python main.py --debug plugins list