# Creating Plugins for Hottopoteto

This guide explains how to create plugins for Hottopoteto to extend its functionality with new link types, utilities, and integrations.

## Plugin Structure

Every plugin must follow this standard directory structure:

```
plugins/plugin_name/ # Plugin root directory 
├── __init__.py # Registration code 
├── plugin.yaml # OR plugin.json - Plugin configuration 
├── links/ # Plugin link handlers 
│ └── __init__.py 
└── README.md # Plugin documentation
```

The `plugin.yaml` or `plugin.json` file is required and must contain:

```yaml
name: "plugin_name"
version: "1.0.0"
description: "Description of what this plugin does"
entry_points:
  links:
    - link_type: "plugin_name.link_type"
      handler: "plugin_name.links.handler_class"
```

A plugin consists of the following components:

1. **Manifest**: Metadata about the plugin
2. **Link Handlers**: Classes that implement link type behavior
3. **Schemas**: JSON schemas for validating link configurations
4. **Requirements**: Dependencies needed by the plugin

Example plugin directory structure:
```
plugins/my_plugin/               # Plugin root directory
├── __init__.py                  # Registration code
├── links.py                     # Link handler implementations
├── schemas/                     # JSON schemas 
│   └── __init__.py
├── manifest.json                # Plugin metadata
└── requirements.txt             # Dependencies
```

## Creating a Plugin

### 1. Set Up the Plugin Directory

Create a directory for your plugin:

```bash
mkdir -p hottopoteto/plugins/my_plugin
```

### 2. Create the Manifest

Create a `manifest.json` file:

```json
{
  "name": "my_plugin",
  "version": "0.1.0",
  "description": "Description of my plugin",
  "author": "Your Name",
  "requirements": ["package>=1.0.0"],
  "entry_points": {
    "link_handlers": ["links.py"]
  }
}
```

### 3. Register the Plugin

Create an `__init__.py` file:

```python
from core.registry import PackageRegistry

def initialize():
    """Initialize plugin."""
    # Any setup code here
    return True

# Register with current package
PackageRegistry.register_plugin_from_package(
    "current_package",  # If standalone, use "core"
    "my_plugin",
    __name__
)
```

### 4. Implement Link Handlers

Create a `links.py` file:

```python
from typing import Dict, Any, ClassVar
from core.links import LinkHandler, register_link_type

class MyLinkHandler(LinkHandler):
    """Handler for my custom link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the link."""
        # Implementation
        result = {}  # Do something with link_config
        return {"data": result}
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for this link type."""
        return {
            "type": "object",
            "properties": {
                "parameter": {
                    "type": "string",
                    "description": "A parameter for this link"
                }
            }
        }

# Register the link type
register_link_type("my_plugin.operation", MyLinkHandler)
```

## Testing Your Plugin

Test your plugin using a simple recipe:

```yaml
name: "Plugin Test"
description: "Testing my plugin"
version: "1.0"
links:
  - name: "Test_Plugin"
    type: "my_plugin.operation"
    parameter: "test value"
```

Run the test:

```bash
python main.py execute --recipe_file recipes/test_plugin.yaml
```

## Plugin Best Practices

1. **Naming Conventions**: Use snake_case for link types and plugin names
2. **Error Handling**: Implement proper error handling in link execution
3. **Documentation**: Document your plugin interfaces and examples
4. **Testing**: Create test recipes for your plugin
5. **Dependencies**: Clearly specify all requirements
6. **Version Compatibility**: Document Hottopoteto version compatibility

## Packaging Your Plugin

For distributing your plugin, create a Python package:

```bash
python main.py packages create my_package --plugin my_plugin
```

See the [Creating Packages](creating_packages.md) guide for details.
