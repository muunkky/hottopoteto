# In lexicon/schema/__init__.py
import os
import json
from typing import Dict, Any

def get_word_schema() -> Dict[str, Any]:
    """Load and return the word schema"""
    schema_path = os.path.join(os.path.dirname(__file__), "word_schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_schema(domain: str, schema_name: str) -> Dict[str, Any]:
    """
    Load a schema by domain and name.
    
    Args:
        domain: The domain the schema belongs to (e.g., 'conlang')
        schema_name: The name of the schema file without extension
        
    Returns:
        Dict[str, Any]: The loaded schema as a dictionary
    """
    # First try domain-specific schema
    domain_schema_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),  # Go up to lexicon/
        "domains", domain, "schemas", f"{schema_name}.json"
    )
    
    # Fall back to general schema directory if domain-specific doesn't exist
    general_schema_path = os.path.join(
        os.path.dirname(__file__), f"{schema_name}.json"
    )
    
    # Try domain-specific first
    if os.path.exists(domain_schema_path):
        with open(domain_schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    # Fall back to general schema
    elif os.path.exists(general_schema_path):
        with open(general_schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    else:
        raise FileNotFoundError(
            f"Schema '{schema_name}' not found for domain '{domain}'"
        )