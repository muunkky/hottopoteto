"""
Schema extension utilities for enhancing recipes with models
"""
import json
import logging
from typing import Dict, Any, Optional, List, Union
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

def resolve_schema_reference(ref: str) -> Dict[str, Any]:
    """
    Resolve a schema reference to a concrete schema.
    
    Args:
        ref: Schema reference string (e.g. "users.profile")
        
    Returns:
        Schema definition
    """
    from core.registration import get_domain_schema
    
    # If it contains a dot, it's a domain.schema reference
    if "." in ref:
        domain, schema_name = ref.split(".", 1)
        schema = get_domain_schema(domain, schema_name)
        if schema:
            return schema
            
    # Otherwise, try direct registry lookup
    from core.schemas import get_schema
    schema = get_schema(ref)
    if schema:
        return schema
        
    logger.error(f"Schema reference not found: {ref}")
    return {"type": "object", "properties": {}}

def extend_schema(base_schema: Union[str, Dict[str, Any]], 
                extensions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extend a base schema with additional properties.
    
    Args:
        base_schema: Base schema or reference
        extensions: Extensions to apply
        
    Returns:
        Extended schema
    """
    # Resolve base schema if it's a reference
    if isinstance(base_schema, str):
        base = resolve_schema_reference(base_schema)
    else:
        base = base_schema.copy()
    
    # Extend properties
    if "properties" in extensions:
        if "properties" not in base:
            base["properties"] = {}
        for prop, schema in extensions["properties"].items():
            base["properties"][prop] = schema
    
    # Extend required fields
    if "required" in extensions:
        if "required" not in base:
            base["required"] = []
        for field in extensions["required"]:
            if field not in base["required"]:
                base["required"].append(field)
    
    # Handle other top-level properties
    for key, value in extensions.items():
        if key not in ["properties", "required"]:
            base[key] = value
    
    return base

def apply_schema_reference(link_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process schema references in a link configuration.
    
    Args:
        link_config: Link configuration from recipe
        
    Returns:
        Link configuration with resolved schemas
    """
    if "output_schema" not in link_config:
        return link_config
    
    output_schema = link_config["output_schema"]
    
    # Handle $ref reference
    if isinstance(output_schema, dict) and "$ref" in output_schema:
        ref = output_schema["$ref"]
        resolved = resolve_schema_reference(ref)
        
        # Keep other properties from the original schema
        for key, value in output_schema.items():
            if key != "$ref":
                resolved[key] = value
                
        link_config["output_schema"] = resolved
    
    # Handle base schema + extensions
    elif isinstance(output_schema, dict) and "base" in output_schema:
        base = output_schema["base"]
        
        # Create a copy without the base property
        extensions = {k:v for k,v in output_schema.items() if k != "base"}
        
        # Extend the base schema
        link_config["output_schema"] = extend_schema(base, extensions)
    
    # Handle _validate_against property
    elif isinstance(output_schema, dict) and "_validate_against" in output_schema:
        validate_against = output_schema["_validate_against"]
        resolved = resolve_schema_reference(validate_against)
        
        # Remove the _validate_against property
        output_schema = {k:v for k,v in output_schema.items() if k != "_validate_against"}
        
        # Store both schemas
        link_config["output_schema"] = output_schema
        link_config["_validation_schema"] = resolved
    
    return link_config

def register_schema_processor(executor):
    """Register schema processing with the executor."""
    # Store original _execute_link method
    original_execute_link = executor._execute_link
    
    # Replace with schema-processing version
    def schema_processing_execute_link(link_config):
        # Process schema references
        processed_config = apply_schema_reference(link_config)
        
        # Call original method
        result = original_execute_link(processed_config)
        
        # Validate against _validation_schema if present
        if "_validation_schema" in processed_config and result:
            try:
                data = result.get("data", {})
                validate(instance=data, schema=processed_config["_validation_schema"])
            except ValidationError as e:
                logger.warning(f"Output validation failed: {e}")
                
        return result
        
    executor._execute_link = schema_processing_execute_link
