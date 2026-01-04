"""
Link handlers for the storage domain
"""
from typing import Dict, Any, List, Optional
import logging
from core.links import LinkHandler, register_link_type
# Update import to new location
from .functions import Repository, save_entity, get_entity, query_entities, delete_entity
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID, optionally with prefix"""
    uid = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix.lower()}-{uid}"
    return uid

class StorageSaveLink(LinkHandler):
    """Handler for storage.save link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the storage.save link."""
        collection = link_config.get("collection")
        data_source = link_config.get("data")
        metadata_source = link_config.get("metadata", {})
        
        # Extract and render templates in data and metadata before saving
        data = cls._extract_data(data_source, context)
        metadata = cls._extract_data(metadata_source, context)
        
        # Use the domain function for saving entities
        result = save_entity(collection, data, metadata)
        
        return {
            "raw": str(result),
            "data": result
        }
    
    @classmethod
    def _extract_data(cls, data_source, context):
        """
        Extract and render templates in data recursively.
        
        Handles:
        - Template strings: "{{ var }}" → rendered value
        - Nested dicts: {"key": {"nested": "{{ var }}"}}
        - Lists: ["{{ var1 }}", "literal", "{{ var2 }}"]
        - Non-string values: numbers, booleans, None (preserved as-is)
        
        Args:
            data_source: Data to extract/render (dict, list, str, or primitive)
            context: Jinja2 template context with recipe memory
            
        Returns:
            Data with all templates rendered
        """
        from jinja2 import Environment, UndefinedError
        
        # Handle None
        if data_source is None:
            return None
        
        # Handle template strings
        if isinstance(data_source, str):
            # Only process if it looks like a template
            if "{{" in data_source and "}}" in data_source:
                try:
                    env = Environment()
                    template = env.from_string(data_source)
                    
                    # Add helper functions to context
                    def now():
                        return datetime.now().isoformat()
                    
                    context_with_funcs = {**context, "now": now}
                    rendered = template.render(**context_with_funcs)
                    
                    logger.debug(f"Rendered template: '{data_source}' → '{rendered}'")
                    return rendered
                    
                except UndefinedError as e:
                    # Undefined variable - return empty string (Jinja2 default)
                    logger.warning(f"Undefined variable in template '{data_source}': {e}")
                    return ""
                except Exception as e:
                    # Other template errors - return original string
                    logger.error(f"Error rendering template '{data_source}': {e}")
                    return data_source
            else:
                # Not a template - return as-is
                return data_source
        
        # Handle dictionaries recursively
        elif isinstance(data_source, dict):
            rendered_dict = {}
            for key, value in data_source.items():
                # Recursively render each value
                rendered_dict[key] = cls._extract_data(value, context)
            return rendered_dict
        
        # Handle lists recursively
        elif isinstance(data_source, list):
            rendered_list = []
            for item in data_source:
                # Recursively render each item
                rendered_list.append(cls._extract_data(item, context))
            return rendered_list
        
        # Handle other types (int, float, bool, etc.) - return as-is
        else:
            return data_source

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type"""
        return {
            "type": "object",
            "required": ["type", "collection", "data"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["storage.save"],
                    "description": "Link type"
                },
                "collection": {
                    "type": "string",
                    "description": "Storage collection name"
                },
                "data": {
                    "oneOf": [
                        {"type": "object", "description": "Data to save"},
                        {"type": "string", "description": "Reference to data from another link"}
                    ],
                    "description": "Data to save"
                },
                "id": {
                    "type": "string",
                    "description": "Optional entity ID"
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional entity metadata"
                }
            }
        }

class StorageGetLink(LinkHandler):
    """Handler for storage.get link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the storage.get link."""
        collection = link_config.get("collection")
        entity_id = link_config.get("id")
        
        # Use the domain function for getting entities
        result = get_entity(collection, entity_id)
        
        return {
            "raw": str(result),
            "data": result
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type"""
        return {
            "type": "object",
            "required": ["type", "collection", "id"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["storage.get"],
                    "description": "Link type"
                },
                "collection": {
                    "type": "string",
                    "description": "Storage collection name"
                },
                "id": {
                    "type": "string",
                    "description": "Entity ID to retrieve"
                }
            }
        }

class StorageQueryLink(LinkHandler):
    """Link handler for querying data from storage"""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the storage.query link"""
        logger.info(f"Executing storage.query link: {link_config.get('name')}")
        
        try:
            # Extract parameters
            collection = link_config.get("collection")
            if not collection:
                return {
                    "raw": None,
                    "data": {"error": "Collection is required", "success": False}
                }
                
            # Extract filter criteria
            filter_criteria = link_config.get("filter", {})
            limit = link_config.get("limit")
            skip = link_config.get("skip")
            
            # Create repository for the collection
            repository = Repository(collection)
            
            # Query entities
            results = repository.query(filter_criteria)
            
            # Apply skip and limit if provided
            if skip:
                results = results[skip:]
            if limit:
                results = results[:limit]
                
            return {
                "raw": None,
                "data": {
                    "success": True,
                    "data": results,
                    "count": len(results)
                }
            }
        except Exception as e:
            logger.error(f"Error querying entities: {e}")
            return {
                "raw": None,
                "data": {
                    "success": False,
                    "message": f"Error querying entities: {str(e)}"
                }
            }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type"""
        return {
            "type": "object",
            "required": ["type", "collection"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["storage.query"],
                    "description": "Link type"
                },
                "collection": {
                    "type": "string",
                    "description": "Storage collection name"
                },
                "filter": {
                    "type": "object", 
                    "description": "Query filter criteria"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results"
                },
                "skip": {
                    "type": "integer",
                    "description": "Number of results to skip"
                }
            }
        }

class StorageDeleteLink(LinkHandler):
    """Handler for storage.delete link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the storage.delete link."""
        collection = link_config.get("collection")
        entity_id = link_config.get("id")
        
        # Use the domain function for deleting entities
        result = delete_entity(collection, entity_id)
        
        return {
            "raw": str(result),
            "data": result
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type"""
        return {
            "type": "object",
            "required": ["type", "collection", "id"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["storage.delete"],
                    "description": "Link type"
                },
                "collection": {
                    "type": "string",
                    "description": "Storage collection name"
                },
                "id": {
                    "type": "string", 
                    "description": "Entity ID to delete"
                }
            }
        }

# Register the link types
register_link_type("storage.save", StorageSaveLink)
register_link_type("storage.get", StorageGetLink)
register_link_type("storage.query", StorageQueryLink)
register_link_type("storage.delete", StorageDeleteLink)
