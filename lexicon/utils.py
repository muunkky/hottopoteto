import os
import json
import uuid
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

def generate_word_id(eldorian_word: str) -> str:
    """Generate a unique word ID based on the Eldorian word."""
    base = eldorian_word.lower().replace(' ', '-')
    return f"{base}-{uuid.uuid4().hex[:4]}"

def fix_common_json_errors(text: str) -> str:
    """Fix common JSON formatting errors in text."""
    fixed = text
    
    # Common keys that might be single-quoted
    single_quoted_keys = [
        "word", "english", "eldorian", "part_of_speech", 
        "ipa", "meaning", "language"
    ]
    
    # Replace single quotes with double quotes for known keys
    for key in single_quoted_keys:
        fixed = fixed.replace(f"'{key}':", f'"{key}":')
        
    # Fix JavaScript-style comments
    fixed = re.sub(r'//.*?\n', '', fixed)
    fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
    
    # Fix unquoted keys
    fixed = re.sub(r'([{,])\s*([a-zA-Z0-9_]+):', r'\1"\2":', fixed)
    
    # Fix trailing commas
    fixed = re.sub(r',\s*([\}\]])', r'\1', fixed)
    
    return fixed

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    Values in dict2 override those in dict1, except for nested dicts
    which are merged recursively.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
            
    return result

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
        print(f"Error loading JSON file {file_path}: {e}")
        return default

def repair_word_entry(word_data: Dict, schema: Dict) -> Dict:
    """
    Automatically repair a word entry to match the schema.
    
    Args:
        word_data: The word data to repair
        schema: The schema to validate against
        
    Returns:
        Dict: The repaired word data
    """
    repaired = word_data.copy()
    
    required_fields = schema.get("required", [])
    schema_props = schema.get("properties", {})
    for field in required_fields:
        if field not in repaired:
            # Use custom defaults for known fields
            if field == "word_id" and "eldorian" in repaired and repaired.get("eldorian"):
                repaired["word_id"] = generate_word_id(repaired["eldorian"])
            elif field == "core":
                repaired["core"] = {
                    "part_of_speech": "noun",
                    "pronunciation": {"ipa": ""},
                    "syllables": [],
                    "definitions": []
                }
            elif field == "metadata":
                repaired["metadata"] = {
                    "schema_version": "1.0",
                    "created_at": datetime.now().isoformat()
                }
            else:
                # Use expected type from schema if available
                expected = schema_props.get(field, {}).get("type", "string")
                if expected == "object":
                    repaired[field] = {}
                elif expected == "array":
                    repaired[field] = []
                else:
                    repaired[field] = ""
    
    # Convert any datetime values in metadata
    if "metadata" in repaired:
        for time_field in ["created_at", "updated_at"]:
            if time_field in repaired["metadata"] and isinstance(repaired["metadata"][time_field], datetime):
                repaired["metadata"][time_field] = repaired["metadata"][time_field].isoformat()
    
    # Handle generation_data timestamps if present
    if "generation_data" in repaired and "timestamp" in repaired["generation_data"]:
        if isinstance(repaired["generation_data"]["timestamp"], datetime):
            repaired["generation_data"]["timestamp"] = repaired["generation_data"]["timestamp"].isoformat()
    
    logging.info("Repaired word entry to conform to schema")
    return repaired