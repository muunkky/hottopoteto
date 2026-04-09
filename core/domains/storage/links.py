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

class StorageInitLink(LinkHandler):
    """
    Handler for storage.init link type.
    
    Creates a "working document" that persists across recipe execution.
    Part of DOCENRICH Sprint - Schema-Driven Document Enrichment.
    
    The storage.init link:
    - Creates a document with unique ID
    - Loads and attaches schema for downstream LLM links
    - Initializes fields with initial_data or null
    - Persists to storage for future storage.update references
    
    Example configuration:
        - name: "Working_Doc"
          type: "storage.init"
          collection: "eldorian_words"
          schema:
            file: "schemas/eldorian_word.yaml"
          initial_data:
            english_word: "{{ user_input }}"
    
    Output structure:
        {
            "raw": "Initialized document doc-abc123",
            "data": {
                "id": "doc-abc123",
                "collection": "eldorian_words",
                "schema": { ... },  # Full schema for downstream reference
                "data": { ... }     # Current document state
            }
        }
    """
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the storage.init link."""
        logger.info(f"Executing storage.init link: {link_config.get('name')}")
        
        try:
            # Extract collection (required)
            collection = link_config.get("collection")
            if not collection:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "Collection is required for storage.init"
                    }
                }
            
            # Resolve schema
            schema_ref = link_config.get("schema")
            schema = cls._resolve_schema(schema_ref, context)
            if schema is None:
                schema = {"type": "object", "properties": {}}
            
            # Extract and render initial_data
            initial_data_source = link_config.get("initial_data", {})
            initial_data = cls._extract_data(initial_data_source, context)
            
            # Initialize document data from schema
            data = cls._initialize_from_schema(schema, initial_data)
            
            # Generate unique document ID
            doc_id = generate_id("doc")
            
            # Create entity for storage
            entity = {
                "id": doc_id,
                "data": data,
                "metadata": {
                    "schema": schema,
                    "collection": collection,
                    "initialized_at": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to repository
            repository = Repository(collection)
            success = repository.save(doc_id, entity)
            
            if success:
                return {
                    "raw": f"Initialized document {doc_id}",
                    "data": {
                        "id": doc_id,
                        "collection": collection,
                        "schema": schema,
                        "data": data
                    }
                }
            else:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": f"Failed to save document {doc_id}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in storage.init: {e}")
            return {
                "raw": None,
                "data": {
                    "success": False,
                    "error": str(e)
                }
            }
    
    @classmethod
    def _resolve_schema(cls, schema_ref: Any, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Resolve schema from file reference or inline definition.
        
        Args:
            schema_ref: Schema reference (file reference dict, inline schema, or None)
            context: Execution context (unused but available for future template support)
            
        Returns:
            Resolved schema dictionary or None
        """
        if schema_ref is None:
            return None
        
        # Use the schema resolution from core.schemas
        from core.schemas import resolve_schema_reference, SchemaNotFoundError, SchemaValidationError
        
        try:
            return resolve_schema_reference(schema_ref)
        except (SchemaNotFoundError, SchemaValidationError) as e:
            logger.error(f"Schema resolution error: {e}")
            raise
    
    @classmethod
    def _initialize_from_schema(
        cls, 
        schema: Dict[str, Any], 
        initial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Initialize document data from schema with initial values.
        
        Properties defined in schema but not in initial_data are set to None.
        
        Args:
            schema: JSON Schema with properties
            initial_data: Pre-populated field values
            
        Returns:
            Initialized data dictionary
        """
        data = {}
        
        # Get properties from schema
        properties = schema.get("properties", {})
        
        for prop_name in properties:
            if prop_name in initial_data:
                data[prop_name] = initial_data[prop_name]
            else:
                data[prop_name] = None
        
        # Also include any initial_data fields not in schema
        for key, value in initial_data.items():
            if key not in data:
                data[key] = value
        
        return data

    @classmethod
    def _extract_data(cls, data_source: Any, context: Dict[str, Any]) -> Any:
        """
        Extract and render templates in data recursively.

        Uses StrictUndefined so that missing template variables raise
        UndefinedError rather than silently expanding to empty string.
        """
        from jinja2 import Environment, StrictUndefined

        if data_source is None:
            return None

        if isinstance(data_source, str):
            if "{{" in data_source and "}}" in data_source:
                def now():
                    return datetime.now().isoformat()

                env = Environment(undefined=StrictUndefined)
                template = env.from_string(data_source)
                context_with_funcs = {**context, "now": now}
                rendered = template.render(**context_with_funcs)
                return rendered
            else:
                return data_source

        elif isinstance(data_source, dict):
            return {key: cls._extract_data(value, context) for key, value in data_source.items()}

        elif isinstance(data_source, list):
            return [cls._extract_data(item, context) for item in data_source]

        else:
            return data_source

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type."""
        return {
            "type": "object",
            "required": ["type", "collection"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["storage.init"],
                    "description": "Link type"
                },
                "collection": {
                    "type": "string",
                    "description": "Storage collection name"
                },
                "schema": {
                    "oneOf": [
                        {
                            "type": "object",
                            "description": "Inline JSON Schema"
                        },
                        {
                            "type": "object",
                            "properties": {
                                "file": {"type": "string"}
                            },
                            "required": ["file"],
                            "description": "File reference to schema"
                        }
                    ],
                    "description": "JSON Schema for document structure"
                },
                "initial_data": {
                    "type": "object",
                    "description": "Initial data to populate document fields"
                }
            }
        }


class StorageUpdateLink(LinkHandler):
    """
    Handler for storage.update link type.
    
    Updates an existing document created by storage.init by merging new data.
    Part of DOCENRICH Sprint - Schema-Driven Document Enrichment.
    
    The storage.update link:
    - Retrieves existing document by document_id
    - Merges new data into existing data (default) or replaces
    - Validates merged data against stored schema
    - Persists updated document
    - Returns updated document state for downstream links
    
    Example configuration:
        - name: "Update_Origins"
          type: "storage.update"
          document_id: "{{ Working_Doc.data.id }}"
          collection: "{{ Working_Doc.data.collection }}"
          data:
            origin_words: "{{ Extract_Origins.data }}"
          merge: true  # Default - merge into existing
    
    Output structure:
        {
            "raw": "Updated document doc-abc123",
            "data": {
                "id": "doc-abc123",
                "collection": "eldorian_words",
                "schema": { ... },
                "data": { ... }  # Updated document state
            }
        }
    """
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the storage.update link."""
        logger.info(f"Executing storage.update link: {link_config.get('name')}")
        
        try:
            # Extract and render document_id (required)
            document_id = link_config.get("document_id")
            if not document_id:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "document_id is required for storage.update"
                    }
                }
            document_id = cls._render_template(document_id, context)
            
            # Extract collection (required)
            collection = link_config.get("collection")
            if not collection:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "collection is required for storage.update"
                    }
                }
            collection = cls._render_template(collection, context)
            
            # Get existing document
            repository = Repository(collection)
            existing = repository.get(document_id)
            
            if not existing:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": f"Document not found: {document_id}"
                    }
                }
            
            # Extract and render new data
            new_data_source = link_config.get("data", {})
            new_data = cls._extract_data(new_data_source, context)
            
            # Get merge settings
            merge = link_config.get("merge", True)
            array_merge = link_config.get("array_merge", "replace")
            
            # Get existing data and schema
            existing_data = existing.get("data", {})
            metadata = existing.get("metadata", {})
            schema = metadata.get("schema", {})
            
            # Merge or replace
            if merge:
                updated_data = cls._deep_merge(existing_data, new_data, array_merge)
            else:
                updated_data = new_data
            
            # Validate against schema if present
            if schema:
                validation_error = cls._validate_against_schema(updated_data, schema)
                if validation_error:
                    return {
                        "raw": None,
                        "data": {
                            "success": False,
                            "error": f"Schema validation failed: {validation_error}"
                        }
                    }
            
            # Update metadata with timestamp
            updated_metadata = {**metadata, "updated_at": datetime.now().isoformat()}
            
            # Create updated entity
            updated_entity = {
                "id": document_id,
                "data": updated_data,
                "metadata": updated_metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save updated document
            success = repository.save(document_id, updated_entity)
            
            if success:
                return {
                    "raw": f"Updated document {document_id}",
                    "data": {
                        "id": document_id,
                        "collection": collection,
                        "schema": schema,
                        "data": updated_data
                    }
                }
            else:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": f"Failed to save updated document {document_id}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in storage.update: {e}")
            return {
                "raw": None,
                "data": {
                    "success": False,
                    "error": str(e)
                }
            }
    
    @classmethod
    def _render_template(cls, value: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 template string."""
        if not isinstance(value, str) or "{{" not in value:
            return value

        from jinja2 import Environment, StrictUndefined
        env = Environment(undefined=StrictUndefined)
        template = env.from_string(value)
        return template.render(**context)

    @classmethod
    def _extract_data(cls, data_source: Any, context: Dict[str, Any]) -> Any:
        """
        Extract and render templates in data recursively.

        Uses StrictUndefined so that missing template variables raise
        UndefinedError rather than silently expanding to empty string.
        """
        from jinja2 import Environment, StrictUndefined

        if data_source is None:
            return None

        if isinstance(data_source, str):
            if "{{" in data_source and "}}" in data_source:
                def now():
                    return datetime.now().isoformat()

                env = Environment(undefined=StrictUndefined)
                template = env.from_string(data_source)
                context_with_funcs = {**context, "now": now}
                rendered = template.render(**context_with_funcs)
                return rendered
            else:
                return data_source

        elif isinstance(data_source, dict):
            return {key: cls._extract_data(value, context) for key, value in data_source.items()}

        elif isinstance(data_source, list):
            return [cls._extract_data(item, context) for item in data_source]

        else:
            return data_source

    @classmethod
    def _deep_merge(
        cls, 
        base: Dict[str, Any], 
        updates: Dict[str, Any],
        array_merge: str = "replace"
    ) -> Dict[str, Any]:
        """
        Deep merge updates into base dictionary.
        
        Args:
            base: Original dictionary
            updates: Dictionary with updates to merge
            array_merge: How to handle arrays - "replace" (default) or "append"
            
        Returns:
            Merged dictionary
        """
        result = dict(base)  # Shallow copy of base
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = cls._deep_merge(result[key], value, array_merge)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # Handle arrays based on merge mode
                if array_merge == "append":
                    result[key] = result[key] + value
                else:
                    result[key] = value
            else:
                # Replace value (including None -> value)
                result[key] = value
        
        return result
    
    @classmethod
    def _validate_against_schema(cls, data: Dict[str, Any], schema: Dict[str, Any]) -> Optional[str]:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema
            
        Returns:
            Error message if validation fails, None if valid
        """
        try:
            import jsonschema
            jsonschema.validate(instance=data, schema=schema)
            return None
        except jsonschema.ValidationError as e:
            return str(e.message)
        except Exception as e:
            logger.warning(f"Schema validation warning: {e}")
            return None  # Don't fail on schema issues
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type."""
        return {
            "type": "object",
            "required": ["type", "document_id", "collection"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["storage.update"],
                    "description": "Link type"
                },
                "document_id": {
                    "type": "string",
                    "description": "ID of document to update (supports templates)"
                },
                "collection": {
                    "type": "string",
                    "description": "Storage collection name"
                },
                "data": {
                    "type": "object",
                    "description": "Data to merge/replace in document"
                },
                "merge": {
                    "type": "boolean",
                    "default": True,
                    "description": "If true (default), merge with existing data. If false, replace."
                },
                "array_merge": {
                    "type": "string",
                    "enum": ["replace", "append"],
                    "default": "replace",
                    "description": "How to handle arrays - replace (default) or append"
                }
            }
        }


# Register the link types
register_link_type("storage.save", StorageSaveLink)
register_link_type("storage.get", StorageGetLink)
register_link_type("storage.query", StorageQueryLink)
register_link_type("storage.delete", StorageDeleteLink)
register_link_type("storage.init", StorageInitLink)
register_link_type("storage.update", StorageUpdateLink)
