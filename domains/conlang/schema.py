"""
Schema definitions for the conlang domain.
"""
from typing import Dict, Any

# Word schema definition
WORD_SCHEMA = {
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
                },
                "definitions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["meaning"],
                        "properties": {
                            "meaning": {"type": "string"},
                            "domain": {"type": "string"},
                            "register": {"type": "string"},
                            "examples": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
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
        "etymology": {
            "type": "object",
            "properties": {
                "origin_words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "language": {"type": "string"},
                            "meaning": {"type": "string"}
                        }
                    }
                }
            }
        },
        "relationships": {
            "type": "object"
        },
        "usage_examples": {
            "type": "array",
            "items": {"type": "string"}
        },
        "metadata": {
            "type": "object",
            "required": ["schema_version"],
            "properties": {
                "schema_version": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}

# Function to get the currently supported word schema
def get_word_schema() -> Dict[str, Any]:
    """Get the current word schema definition."""
    return WORD_SCHEMA
