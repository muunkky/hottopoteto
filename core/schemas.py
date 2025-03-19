"""
JSON schema registry and utilities.
"""
from typing import Dict, Any, Optional
import logging
import json
import os

logger = logging.getLogger(__name__)

# Dictionary to store registered schemas
_schemas = {}

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
