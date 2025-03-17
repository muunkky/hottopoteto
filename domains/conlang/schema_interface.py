"""
Schema interface implementation for the conlang domain.
"""
from typing import Dict, Any, Optional
import json
import os
from core.domains import register_domain_schema

# Core schema definitions for the conlang domain
SCHEMAS = {
    "word_schema": {
        "type": "object",
        "required": ["id", "eldorian", "english", "core", "metadata"],
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique identifier for this word entry"
            },
            "eldorian": {
                "type": "string",
                "description": "The word in the constructed language"
            },
            "english": {
                "type": "string",
                "description": "The English translation/meaning"
            },
            "core": {
                "type": "object",
                "required": ["part_of_speech", "pronunciation", "syllables"],
                "properties": {
                    "part_of_speech": {
                        "type": "string",
                        "enum": ["noun", "verb", "adjective", "adverb", "pronoun", "preposition"],
                        "description": "Grammatical category of the word"
                    },
                    "pronunciation": {
                        "type": "object",
                        "properties": {
                            "ipa": {"type": "string"},
                            "stress_pattern": {"type": "string"}
                        }
                    },
                    "syllables": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "grammatical_properties": {
                "type": "object",
                "required": ["$type"],
                "properties": {
                    "$type": {"type": "string"}
                }
            },
            "metadata": {
                "type": "object",
                "required": ["schema_version"],
                "properties": {
                    "schema_version": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            }
        }
    },
    
    "phrase_schema": {
        "type": "object",
        "required": ["id", "eldorian", "english", "metadata"],
        "properties": {
            "id": {
                "type": "string", 
                "description": "Unique identifier for this phrase"
            },
            "eldorian": {
                "type": "string",
                "description": "The phrase in the constructed language"
            },
            "english": {
                "type": "string",
                "description": "The English translation"
            },
            "words": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "word_id": {"type": "string"},
                        "form": {"type": "string"}
                    }
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "schema_version": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                }
            }
        }
    }
}

def register_schemas() -> None:
    """Register all conlang schemas with the domain system."""
    for schema_name, schema in SCHEMAS.items():
        register_domain_schema("conlang", schema_name, schema)

def get_schema(schema_name: str) -> Optional[Dict[str, Any]]:
    """Get a schema by name."""
    return SCHEMAS.get(schema_name)

def save_schemas_to_files(output_dir: str) -> None:
    """Save all schemas to JSON files in the specified directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    for schema_name, schema in SCHEMAS.items():
        file_path = os.path.join(output_dir, f"{schema_name}.json")
        with open(file_path, "w") as f:
            json.dump(schema, f, indent=2)

# Register schemas when module is loaded
register_schemas()
