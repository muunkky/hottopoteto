"""
JSON schema registry and utilities.

This module provides:
1. Schema registry for named schemas
2. Schema file loading from templates/schemas/
3. Schema reference resolution for recipe configs

Part of DOCENRICH Sprint - Schema-Driven Document Enrichment.
See ADR-0006 for architectural context.
"""
from typing import Dict, Any, Optional, Union
import logging
import json
import os
import yaml

logger = logging.getLogger(__name__)

# Dictionary to store registered schemas
_schemas = {}

# Cache for loaded schema files
_schema_cache: Dict[str, Dict[str, Any]] = {}


class SchemaError(Exception):
    """Base exception for schema-related errors."""
    pass


class SchemaNotFoundError(SchemaError):
    """Raised when a schema file cannot be found."""
    pass


class SchemaValidationError(SchemaError):
    """Raised when a schema file contains invalid JSON Schema."""
    pass

def register_schema(name: str, schema: Dict[str, Any]) -> None:
    """
    Register a schema with the registry.
    
    Args:
        name: Schema name (usually in format domain.entity)
        schema: JSON schema definition
    """
    _schemas[name] = schema
    logger.debug(f"Registered schema: {name}")
    
def get_schema(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a schema by name.
    
    Args:
        name: Schema name
        
    Returns:
        Schema definition or None if not found
    """
    return _schemas.get(name)
    
def list_schemas() -> Dict[str, Dict[str, Any]]:
    """
    Get all registered schemas.
    
    Returns:
        Dictionary of schema name to schema definition
    """
    return _schemas


# =============================================================================
# Schema File Loading (DOCENRICH Sprint)
# =============================================================================

def clear_schema_cache() -> None:
    """Clear the schema file cache. Useful for testing."""
    global _schema_cache
    _schema_cache.clear()


def _validate_schema_structure(schema: Dict[str, Any], file_path: str) -> None:
    """
    Validate that a loaded dictionary is a valid JSON Schema.
    
    Performs basic structural validation without full JSON Schema metaschema
    validation (which would require additional dependencies).
    
    Args:
        schema: The loaded schema dictionary
        file_path: Path to the file (for error messages)
        
    Raises:
        SchemaValidationError: If the schema is invalid
    """
    if not isinstance(schema, dict):
        raise SchemaValidationError(
            f"Schema must be a dictionary, got {type(schema).__name__}: {file_path}"
        )
    
    # Check for basic JSON Schema structure
    # A valid schema should have 'type' or be a boolean schema
    # or have some schema keywords
    valid_keywords = {
        'type', 'properties', 'items', 'required', 'enum', 'const',
        'allOf', 'anyOf', 'oneOf', 'not', '$ref', '$schema', '$id',
        'title', 'description', 'default', 'examples',
        'minimum', 'maximum', 'minLength', 'maxLength',
        'pattern', 'format', 'additionalProperties', 'patternProperties'
    }
    
    if not any(key in schema for key in valid_keywords):
        raise SchemaValidationError(
            f"Schema file does not appear to be a valid JSON Schema "
            f"(no recognized schema keywords): {file_path}"
        )


def load_schema_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON Schema from a file.
    
    Supports both YAML (.yaml, .yml) and JSON (.json) formats.
    Results are cached to avoid repeated disk reads.
    
    Args:
        file_path: Absolute or relative path to the schema file
        
    Returns:
        The parsed JSON Schema as a dictionary
        
    Raises:
        SchemaNotFoundError: If the file doesn't exist
        SchemaValidationError: If the file isn't valid JSON Schema
    """
    # Check cache first
    abs_path = os.path.abspath(file_path)
    if abs_path in _schema_cache:
        logger.debug(f"Schema cache hit: {abs_path}")
        return _schema_cache[abs_path]
    
    # Check file exists
    if not os.path.exists(abs_path):
        raise SchemaNotFoundError(f"Schema file not found: {file_path}")
    
    # Load based on extension
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            if ext in ('.yaml', '.yml'):
                schema = yaml.safe_load(f)
            elif ext == '.json':
                schema = json.load(f)
            else:
                # Default to YAML (more permissive parser)
                schema = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise SchemaValidationError(f"Invalid YAML in schema file {file_path}: {e}")
    except json.JSONDecodeError as e:
        raise SchemaValidationError(f"Invalid JSON in schema file {file_path}: {e}")
    
    # Validate structure
    _validate_schema_structure(schema, file_path)
    
    # Cache and return
    _schema_cache[abs_path] = schema
    logger.debug(f"Loaded and cached schema: {abs_path}")
    
    return schema


def resolve_schema_reference(
    schema_ref: Union[Dict[str, Any], str, None],
    search_dirs: Optional[list] = None
) -> Optional[Dict[str, Any]]:
    """
    Resolve a schema reference to an actual schema dictionary.
    
    Handles four cases:
    1. Domain schema reference: { "$ref": "domain.schema" }
    2. File reference: { "file": "path/to/schema.yaml" }
    3. Inline schema: { "type": "object", ... }
    4. None/empty: Returns None
    
    Args:
        schema_ref: The schema reference from recipe config
        search_dirs: Optional list of directories to search for schema files.
                    If None, uses registered template directories.
        
    Returns:
        The resolved JSON Schema dictionary, or None if no schema
        
    Raises:
        SchemaNotFoundError: If file reference can't be resolved
        SchemaValidationError: If loaded schema is invalid
    """
    if schema_ref is None:
        return None
    
    # Handle domain schema reference ($ref)
    if isinstance(schema_ref, dict) and "$ref" in schema_ref:
        ref_path = schema_ref["$ref"]
        
        # Look up in the central schema registry
        schema = get_schema(ref_path)
        
        if schema is None:
            raise SchemaNotFoundError(
                f"Domain schema not found: {ref_path}. "
                f"Make sure the domain has registered this schema using "
                f"register_domain_schema()."
            )
        
        return schema
    
    # Handle file reference
    if isinstance(schema_ref, dict) and "file" in schema_ref:
        file_ref = schema_ref["file"]
        
        # Get search directories
        if search_dirs is None:
            from core.templates import get_template_directories
            search_dirs = get_template_directories("schemas")
        
        # Search for the file
        for search_dir in search_dirs:
            candidate = os.path.join(search_dir, file_ref)
            if os.path.exists(candidate):
                loaded_schema = load_schema_file(candidate)
                # If the loaded file contains a $ref, resolve it recursively
                if isinstance(loaded_schema, dict) and "$ref" in loaded_schema:
                    return resolve_schema_reference(loaded_schema, search_dirs)
                return loaded_schema
        
        # Also try direct path
        if os.path.exists(file_ref):
            loaded_schema = load_schema_file(file_ref)
            # If the loaded file contains a $ref, resolve it recursively
            if isinstance(loaded_schema, dict) and "$ref" in loaded_schema:
                return resolve_schema_reference(loaded_schema, search_dirs)
            return loaded_schema
        
        raise SchemaNotFoundError(
            f"Schema file not found: {file_ref}. "
            f"Searched in: {search_dirs}"
        )
    
    # Handle inline schema (pass through)
    if isinstance(schema_ref, dict):
        # Validate inline schema
        _validate_schema_structure(schema_ref, "<inline>")
        return schema_ref
    
    # Handle string path (deprecated but supported)
    if isinstance(schema_ref, str):
        logger.warning(
            f"String schema reference '{schema_ref}' is deprecated. "
            f"Use {{ file: '{schema_ref}' }} instead."
        )
        return resolve_schema_reference({"file": schema_ref}, search_dirs)
    
    raise SchemaValidationError(
        f"Invalid schema reference type: {type(schema_ref).__name__}"
    )


def get_schema_property(schema: Dict[str, Any], property_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract a sub-schema from a larger schema by property path.
    
    Useful for extracting just the schema for a specific field
    when doing targeted extraction.
    
    Args:
        schema: The parent schema
        property_path: Dot-separated path to the property (e.g., "properties.origin_words")
        
    Returns:
        The sub-schema at that path, or None if not found
        
    Example:
        >>> schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        >>> get_schema_property(schema, "properties.name")
        {"type": "string"}
    """
    current = schema
    for part in property_path.split('.'):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current if isinstance(current, dict) else None
