"""
Model definitions and schemas for linguistics domain
"""
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from core.models import GenericEntryModel
from datetime import datetime
from core.registration import register_domain_schema
import os
import json

# Word model with combined fields
class Word(GenericEntryModel):
    """A word in a language"""
    spelling: str
    pronunciation: Optional[str] = None
    definition: str
    part_of_speech: str
    language: str
    etymology: Optional[str] = None
    related_words: List[str] = Field(default_factory=list)
    usage_examples: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    cognates: List[str] = Field(default_factory=list)

# Phoneme model
class Phoneme(GenericEntryModel):
    """A phoneme in a language"""
    symbol: str
    features: Dict[str, bool] = Field(default_factory=dict)
    description: Optional[str] = None
    example_words: List[str] = Field(default_factory=list)
    ipa: Optional[str] = None
    sound_type: str = "consonant"
    articulation: Dict[str, str] = Field(default_factory=dict)

# MorphologicalRule model
class MorphologicalRule(GenericEntryModel):
    """A morphological rule in a language"""
    name: str
    description: str
    pattern: str
    replacement: str
    conditions: Dict[str, Any] = Field(default_factory=dict)
    examples: List[Dict[str, str]] = Field(default_factory=list)
    rule_type: str = "inflection"
    applies_to: List[str] = Field(default_factory=list)

# Language model 
class Language(GenericEntryModel):
    """A constructed language"""
    name: str
    code: str
    description: Optional[str] = None
    creator: Optional[str] = None
    creation_date: Optional[datetime] = None
    phonology: Dict[str, Any] = Field(default_factory=dict)
    grammar: Dict[str, Any] = Field(default_factory=dict)
    vocabulary_size: int = 0
    writing_system: Optional[Dict[str, Any]] = None

# Text model
class Text(GenericEntryModel):
    """A text in a constructed language"""
    title: str
    content: str
    language: str
    translation: Optional[str] = None
    notes: Optional[str] = None
    glosses: List[Dict[str, str]] = Field(default_factory=list)

# Register model schemas
register_domain_schema("linguistics", "word", Word.schema())
register_domain_schema("linguistics", "phoneme", Phoneme.schema())
register_domain_schema("linguistics", "language", Language.schema())
register_domain_schema("linguistics", "text", Text.schema())
register_domain_schema("linguistics", "morphological_rule", MorphologicalRule.schema())

# Register additional schemas that don't have corresponding models
register_domain_schema("linguistics", "syllable", {
    "type": "object",
    "required": ["structure", "language"],
    "properties": {
        "structure": {"type": "string", "description": "Syllable structure (e.g., 'CV', 'CVC')"},
        "language": {"type": "string", "description": "Language code"},
        "allowed_onsets": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Allowed onset consonants"
        },
        "allowed_nuclei": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Allowed nucleus vowels"
        },
        "allowed_codas": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Allowed coda consonants"
        }
    }
})

register_domain_schema("linguistics", "orthography", {
    "type": "object",
    "required": ["name", "language"],
    "properties": {
        "name": {"type": "string", "description": "Name of the orthography"},
        "language": {"type": "string", "description": "Language code"},
        "description": {"type": "string", "description": "Description of the orthography"},
        "character_map": {
            "type": "object",
            "description": "Mapping from phonemes to orthographic characters"
        },
        "rules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Orthographic rules"
        }
    }
})

register_domain_schema("linguistics", "phonological_rule", {
    "type": "object",
    "required": ["name", "pattern", "change", "language"],
    "properties": {
        "name": {"type": "string", "description": "Rule name"},
        "language": {"type": "string", "description": "Language code"},
        "pattern": {"type": "string", "description": "Pattern to match"},
        "change": {"type": "string", "description": "Resulting change"},
        "environment": {"type": "string", "description": "Phonological environment"},
        "description": {"type": "string", "description": "Human-readable description"}
    }
})

# Optional: Load additional schemas from JSON files
def load_schema_files():
    """Load and register schemas from JSON files"""
    schema_dir = os.path.join(os.path.dirname(__file__), "schemas")
    if os.path.exists(schema_dir):
        for filename in os.listdir(schema_dir):
            if filename.endswith(".json"):
                schema_name = os.path.splitext(filename)[0]
                schema_path = os.path.join(schema_dir, filename)
                
                with open(schema_path, "r") as f:
                    schema = json.load(f)
                    register_domain_schema("linguistics", schema_name, schema)

# Load any additional schema files
load_schema_files()