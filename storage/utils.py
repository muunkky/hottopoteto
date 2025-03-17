import os
import json
import uuid
import re
import logging
from typing import Dict, Any
from datetime import datetime

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID, optionally with a prefix."""
    if prefix:
        return f"{prefix.lower()}-{uuid.uuid4().hex[:8]}"
    return uuid.uuid4().hex[:12]

def ensure_directory(directory: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)

def safe_load_json(file_path: str, default=None) -> Any:
    """Safely load a JSON file, returning default if an error occurs."""
    if default is None:
        default = {}
        
    if not os.path.exists(file_path):
        return default
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return default

def repair_entry(entry_data: Dict, schema: Dict) -> Dict:
    """
    Automatically repair an entry to match the schema.
    
    Args:
        entry_data: The entry data to repair
        schema: The schema to validate against
        
    Returns:
        Dict: The repaired entry data
    """
    repaired = entry_data.copy()
    
    required_fields = schema.get("required", [])
    schema_props = schema.get("properties", {})
    for field in required_fields:
        if field not in repaired:
            # Use expected type from schema if available
            expected = schema_props.get(field, {}).get("type", "string")
            if expected == "object":
                repaired[field] = {}
            elif expected == "array":
                repaired[field] = []
            else:
                repaired[field] = ""
    
    # Convert any datetime values
    for field in repaired:
        if isinstance(repaired[field], datetime):
            repaired[field] = repaired[field].isoformat()
            
    # Handle nested fields
    for field, value in repaired.items():
        if isinstance(value, dict):
            for subfield, subvalue in value.items():
                if isinstance(subvalue, datetime):
                    repaired[field][subfield] = subvalue.isoformat()
    
    logging.info("Repaired entry to conform to schema")
    return repaired
