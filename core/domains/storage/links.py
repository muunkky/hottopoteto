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
        data = link_config.get("data")
        metadata = link_config.get("metadata", {})
        
        # Use the domain function for saving entities
        result = save_entity(collection, data, metadata)
        
        return {
            "raw": str(result),
            "data": result
        }
    
    @classmethod
    def _extract_data(cls, data_source, context):
        """Extract data from source reference or direct value"""
        logger.info(f"Extracting data from source type: {type(data_source).__name__}")
        
        # Debug the context
        for k, v in context.items():
            if isinstance(v, dict):
                logger.debug(f"Context key: {k}, contains: {list(v.keys())}")
                if 'data' in v:
                    logger.debug(f"  'data' is type: {type(v['data']).__name__}")
        
        if isinstance(data_source, dict):
            # Direct data structure - use it directly
            for k, v in data_source.items():
                if isinstance(v, str) and "{{" in v and "}}" in v:
                    # Template string inside a dict value
                    from jinja2 import Environment
                    env = Environment()
                    template = env.from_string(v)
                    try:
                        # Add now() function to context
                        def now():
                            return datetime.now().isoformat()
                        context_with_funcs = {**context, "now": now}
                        
                        rendered = template.render(**context_with_funcs)
                        data_source[k] = rendered
                    except Exception as e:
                        logger.error(f"Error rendering template in dict value: {e}")
            
            logger.info(f"Using direct data: {data_source}")
            return data_source
            
        elif isinstance(data_source, str) and "{{" in data_source and "}}" in data_source:
            # It's a Jinja template reference
            from jinja2 import Environment
            env = Environment()
            template = env.from_string(data_source)
            
            try:
                # Add now() function to context
                def now():
                    return datetime.now().isoformat()
                context_with_funcs = {**context, "now": now}
                
                # Render the template in context
                rendered = template.render(**context_with_funcs)
                logger.info(f"Template rendered to: {rendered}")
                
                # Try to parse as JSON if it's a string
                try:
                    import json
                    return json.loads(rendered)
                except:
                    # Just return the string if it's not JSON
                    logger.debug(f"Not JSON, returning as content: {rendered}")
                    return {"content": rendered}
                    
            except Exception as e:
                logger.error(f"Error extracting data from template: {e}")
                # Return simple placeholder data rather than None
                return {"error": f"Template error: {str(e)}"}
        
        # Default case - return input as-is or empty dict if None
        logger.info(f"Using default case: {data_source}")
        return data_source or {}

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
