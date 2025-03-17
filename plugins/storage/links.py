"""Storage link type implementation."""
from typing import Dict, Any, Optional
import os
import json
import logging

from core.links import LinkHandler, register_link_type
from storage.repository import Repository
from storage.adapters import get_adapter, StorageAdapter

class StorageLinkHandler(LinkHandler):
    """Handler for storage operations."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a storage operation."""
        operation = link_config.get("operation", "store")
        adapter_config = link_config.get("adapter", {})
        adapter_type = adapter_config.get("type", "file")
        adapter_options = adapter_config.get("config", {})
        
        # Process data with template substitution (handle nested references)
        data = cls._process_data(link_config.get("data", {}), context)
        
        try:
            # Get the adapter
            adapter_class = get_adapter(adapter_type)
            adapter = adapter_class.initialize(adapter_options)
            
            result = {}
            # Execute operation
            if operation == "store":
                # Store data
                id = adapter.store(data)
                result = {"id": id, "stored": True}
            elif operation == "retrieve":
                # Retrieve data
                id = cls._process_template(link_config.get("id", ""), context)
                retrieved_data = adapter.retrieve(id)
                result = {"id": id, "data": retrieved_data}
            elif operation == "update":
                # Update data
                id = cls._process_template(link_config.get("id", ""), context)
                success = adapter.update(id, data)
                result = {"id": id, "updated": success}
            elif operation == "delete":
                # Delete data
                id = cls._process_template(link_config.get("id", ""), context)
                success = adapter.delete(id)
                result = {"id": id, "deleted": success}
            elif operation == "search":
                # Search for data
                query = cls._process_data(link_config.get("query", {}), context)
                matches = adapter.search(query)
                result = {"query": query, "matches": matches, "count": len(matches)}
            else:
                result = {"error": f"Unknown storage operation: {operation}"}
                
            return result
        except Exception as e:
            logging.error(f"Error executing storage operation: {e}")
            return {"error": str(e)}
    
    @classmethod
    def _process_data(cls, data_template, context):
        """Process data values, handling nested structures."""
        if isinstance(data_template, dict):
            result = {}
            for key, value in data_template.items():
                if isinstance(value, (dict, list)):
                    result[key] = cls._process_data(value, context)
                elif isinstance(value, str):
                    result[key] = cls._process_template(value, context)
                else:
                    result[key] = value
            return result
        elif isinstance(data_template, list):
            result = []
            for item in data_template:
                if isinstance(item, (dict, list)):
                    result.append(cls._process_data(item, context))
                elif isinstance(item, str):
                    result.append(cls._process_template(item, context))
                else:
                    result.append(item)
            return result
        else:
            return data_template
    
    @classmethod
    def _process_template(cls, template, context):
        """Process a template string with values from context."""
        if isinstance(template, str) and "{{" in template and "}}" in template:
            # Very simple template processing - in production use a proper template engine
            result = template
            for key, value in context.items():
                if key in context and isinstance(context[key], dict):
                    for subkey, subvalue in context[key].items():
                        if subkey == "data" and isinstance(subvalue, dict):
                            for data_key, data_value in subvalue.items():
                                result = result.replace(
                                    f"{{{{ {key}.data.{data_key} }}}}",
                                    str(data_value)
                                )
                result = result.replace(f"{{{{ {key} }}}}", str(value))
            return result
        return template
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the schema for storage link configuration."""
        return {
            "type": "object",
            "required": ["operation", "adapter"],
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["store", "retrieve", "update", "delete", "search"],
                    "description": "Storage operation to perform"
                },
                "adapter": {
                    "type": "object",
                    "required": ["type"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Storage adapter type (file, sqlite, mongodb, etc.)"
                        },
                        "config": {
                            "type": "object",
                            "description": "Adapter-specific configuration"
                        }
                    }
                },
                "data": {
                    "type": "object",
                    "description": "Data to store/update (for store and update operations)"
                },
                "id": {
                    "type": "string",
                    "description": "ID of the item to retrieve/update/delete"
                },
                "query": {
                    "type": "object",
                    "description": "Query parameters for search operation"
                }
            },
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["store"]}
                        }
                    },
                    "then": {
                        "required": ["data"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["retrieve", "update", "delete"]}
                        }
                    },
                    "then": {
                        "required": ["id"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["update"]}
                        }
                    },
                    "then": {
                        "required": ["data"]
                    }
                },
                {
                    "if": {
                        "properties": {
                            "operation": {"enum": ["search"]}
                        }
                    },
                    "then": {
                        "required": ["query"]
                    }
                }
            ]
        }

# Register the storage link type
register_link_type("storage", StorageLinkHandler)
