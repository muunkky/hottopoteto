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

# Nested models for complex structures
class CaseForm(BaseModel):
    """Declension forms by grammatical case"""
    nominative: Optional[str] = None
    accusative: Optional[str] = None
    genitive: Optional[str] = None
    dative: Optional[str] = None
    instrumental: Optional[str] = None
    locative: Optional[str] = None
    vocative: Optional[str] = None

class Declension(BaseModel):
    """Noun/adjective declension paradigm"""
    declension_class: Optional[str] = Field(None, description="Which declension pattern this follows")
    singular: Optional[CaseForm] = None
    plural: Optional[CaseForm] = None
    dual: Optional[CaseForm] = None

class PersonForm(BaseModel):
    """Verb forms by grammatical person"""
    first_person_singular: Optional[str] = None
    second_person_singular: Optional[str] = None
    third_person_singular: Optional[str] = None
    first_person_plural: Optional[str] = None
    second_person_plural: Optional[str] = None
    third_person_plural: Optional[str] = None

class ImperativeForm(BaseModel):
    """Imperative mood forms"""
    second_person_singular: Optional[str] = None
    second_person_plural: Optional[str] = None

class Participles(BaseModel):
    """Participial forms"""
    present_active: Optional[str] = None
    past_passive: Optional[str] = None
    future_active: Optional[str] = None

class Conjugation(BaseModel):
    """Verb conjugation paradigm"""
    conjugation_class: Optional[str] = Field(None, description="Which conjugation pattern this follows")
    present: Optional[PersonForm] = None
    past: Optional[PersonForm] = None
    future: Optional[PersonForm] = None
    imperative: Optional[ImperativeForm] = None
    subjunctive: Optional[Dict[str, Any]] = None
    conditional: Optional[Dict[str, Any]] = None
    participles: Optional[Participles] = None
    infinitive: Optional[str] = None
    gerund: Optional[str] = None

class Comparison(BaseModel):
    """Degrees of comparison for adjectives/adverbs"""
    positive: Optional[str] = None
    comparative: Optional[str] = None
    superlative: Optional[str] = None
    absolute_superlative: Optional[str] = None

class AlternateForm(BaseModel):
    """Variant form with context"""
    form: Optional[str] = None
    pronunciation: Optional[str] = None
    context: Optional[str] = Field(None, description="When this variant is used (dialectal, archaic, formal, etc.)")

class OriginWord(BaseModel):
    """Etymology source word"""
    word: Optional[str] = None
    meaning: Optional[str] = None
    origin: Optional[str] = Field(None, description="Language or culture of origin")
    date: Optional[str] = Field(None, description="Approximate date or period of borrowing")

class Affix(BaseModel):
    """Morphological affix"""
    affix: Optional[str] = None
    type: Optional[str] = Field(None, description="prefix, suffix, infix, or circumfix")
    meaning: Optional[str] = None
    function: Optional[str] = Field(None, description="derivational or inflectional")

class CompoundElement(BaseModel):
    """Element of a compound word"""
    element: Optional[str] = None
    meaning: Optional[str] = None
    position: Optional[int] = None

class Morphology(BaseModel):
    """Morphological breakdown"""
    roots: Optional[List[str]] = Field(default_factory=list, description="Root morphemes")
    affixes: Optional[List[Affix]] = Field(default_factory=list)
    compound_elements: Optional[List[CompoundElement]] = Field(default_factory=list)

class Meaning(BaseModel):
    """Distinct sense/definition"""
    definition: Optional[str] = None
    sense_number: Optional[int] = None
    examples: Optional[List[str]] = Field(default_factory=list)
    register: Optional[str] = Field(None, description="formal, informal, archaic, poetic, etc.")

class UsageExample(BaseModel):
    """Example sentence"""
    eldorian: Optional[str] = Field(None, description="Sentence in the constructed language")
    translation: Optional[str] = Field(None, description="English translation")
    context: Optional[str] = Field(None, description="Situational context")
    register: Optional[str] = None

class Collocation(BaseModel):
    """Common word combination"""
    phrase: Optional[str] = None
    translation: Optional[str] = None
    type: Optional[str] = Field(None, description="noun_adjective, verb_noun, verb_adverb, preposition_noun, idiom")

class Synonym(BaseModel):
    """Synonym with differentiation"""
    word: Optional[str] = None
    difference: Optional[str] = Field(None, description="How this synonym differs in meaning or usage")

class RelatedWord(BaseModel):
    """Semantically related word"""
    word: Optional[str] = None
    relationship: Optional[str] = Field(None, description="hypernym, hyponym, meronym, holonym, coordinate")

class DerivedWord(BaseModel):
    """Word derived from this word"""
    word: Optional[str] = None
    word_class: Optional[str] = None
    derivation_method: Optional[str] = None
    meaning: Optional[str] = None

class DialectalVariation(BaseModel):
    """Dialectal variant"""
    dialect: Optional[str] = None
    form: Optional[str] = None
    pronunciation: Optional[str] = None
    notes: Optional[str] = None

class IrregularForm(BaseModel):
    """Irregular inflected form"""
    form: Optional[str] = None
    grammatical_category: Optional[str] = None
    notes: Optional[str] = None

class ArgumentRole(BaseModel):
    """Syntactic argument"""
    role: Optional[str] = Field(None, description="agent, patient, theme, experiencer, beneficiary, instrument, location, goal, source")
    case: Optional[str] = None
    required: Optional[bool] = False

class ArgumentStructure(BaseModel):
    """Syntactic argument structure for verbs"""
    valency: Optional[int] = Field(None, description="Number of arguments (0=weather verb, 1=intransitive, 2=transitive, 3=ditransitive)")
    arguments: Optional[List[ArgumentRole]] = Field(default_factory=list)

# Comprehensive Word model - the platonic ideal of a lexicon entry
class Word(GenericEntryModel):
    """
    Comprehensive word model for constructed languages.
    
    This is the domain's definition of what a word IS - everything that can be
    known about a word in a constructed language. Not all fields need to be
    populated for every word; this is the complete schema.
    """
    
    # === BASIC IDENTIFICATION ===
    # Only eldorian_word is required at model level - everything else can be built up over time
    # Recipe-level validation should enforce additional requirements for specific workflows
    eldorian_word: str = Field(description="The canonical form (lemma)")
    english_word: Optional[str] = Field(None, description="The English word being translated")
    language: Optional[str] = Field(default="eldorian", description="Language code")
    pronunciation: Optional[str] = Field(None, description="IPA phonetic transcription")
    alternate_forms: Optional[List[AlternateForm]] = Field(
        default_factory=list,
        description="Variant spellings or pronunciations with context"
    )
    
    # === ETYMOLOGY ===
    origin_words: Optional[List[OriginWord]] = Field(
        default_factory=list,
        description="Source words from which this derives"
    )
    historical_development: Optional[str] = Field(
        None, 
        description="Diachronic evolution of form and meaning"
    )
    
    # === GRAMMATICAL CLASSIFICATION ===
    word_class: Optional[str] = Field(
        None,
        description="Part of speech (noun, verb, adjective, adverb, pronoun, determiner, preposition, conjunction, particle, interjection)"
    )
    grammatical_gender: Optional[str] = Field(
        None,
        description="Grammatical gender (masculine, feminine, neuter, common, animate, inanimate)"
    )
    animacy: Optional[str] = Field(
        None, 
        description="Animacy class (animate, inanimate, divine, abstract)"
    )
    
    # === INFLECTIONAL MORPHOLOGY ===
    declension: Optional[Declension] = Field(
        None,
        description="Noun/adjective declension paradigm by case and number"
    )
    conjugation: Optional[Conjugation] = Field(
        None,
        description="Verb conjugation paradigm by tense, mood, person"
    )
    comparison: Optional[Comparison] = Field(
        None,
        description="Degrees of comparison (positive, comparative, superlative)"
    )
    irregular_forms: Optional[List[IrregularForm]] = Field(
        default_factory=list,
        description="Any irregular inflected forms"
    )
    
    # === DERIVATIONAL MORPHOLOGY ===
    morphology: Optional[Morphology] = Field(
        None,
        description="Morphological breakdown (roots, affixes, compounds)"
    )
    derived_words: Optional[List[DerivedWord]] = Field(
        default_factory=list,
        description="Words derived from this word"
    )
    derives_from: Optional[str] = Field(
        None,
        description="Reference to source word if this is derived"
    )
    
    # === SEMANTICS ===
    meanings: Optional[List[Meaning]] = Field(
        default_factory=list,
        description="Distinct senses/definitions with examples and register"
    )
    connotation: Optional[str] = Field(
        None,
        description="Emotional coloring (positive, negative, neutral, honorific, pejorative, intimate, formal)"
    )
    semantic_fields: Optional[List[str]] = Field(
        default_factory=list,
        description="Semantic domains (e.g., nature.water, emotion.fear)"
    )
    
    # === SYNTAX ===
    argument_structure: Optional[ArgumentStructure] = Field(
        None,
        description="Syntactic argument structure for verbs"
    )
    subcategorization: Optional[str] = Field(
        None,
        description="Types of complements this word takes"
    )
    
    # === USAGE ===
    usage_examples: Optional[List[UsageExample]] = Field(
        default_factory=list,
        description="Example sentences with translation and context"
    )
    collocations: Optional[List[Collocation]] = Field(
        default_factory=list,
        description="Common word combinations"
    )
    frequency: Optional[str] = Field(
        None,
        description="Frequency of use (very_common, common, uncommon, rare, archaic, obsolete)"
    )
    
    # === LEXICAL RELATIONS ===
    synonyms: Optional[List[Synonym]] = Field(
        default_factory=list,
        description="Words with similar meanings and how they differ"
    )
    antonyms: Optional[List[str]] = Field(default_factory=list, description="Opposite meanings")
    related_words: Optional[List[RelatedWord]] = Field(
        default_factory=list,
        description="Semantically related words with relationship type"
    )
    compound_of: Optional[List[str]] = Field(
        default_factory=list,
        description="Constituent words if this is a compound"
    )
    
    # === SOCIOLINGUISTIC ===
    register: Optional[str] = Field(
        None,
        description="Overall register/style level (formal, informal, neutral, archaic, poetic, technical, colloquial, vulgar, literary, ceremonial)"
    )
    dialectal_variations: Optional[List[DialectalVariation]] = Field(
        default_factory=list,
        description="How this word varies across dialects"
    )
    stylistic_notes: Optional[str] = Field(
        None,
        description="Notes on appropriate contexts of use"
    )
    
    # === CULTURAL & PRAGMATIC ===
    cultural_notes: Optional[str] = Field(
        None,
        description="Cultural significance or associations"
    )
    pragmatic_notes: Optional[str] = Field(
        None,
        description="How this word functions in discourse"
    )
    taboos: Optional[str] = Field(None, description="Cultural taboos or restrictions")
    
    # === META ===
    notes: Optional[str] = Field(None, description="General notes or comments")
    references: Optional[List[str]] = Field(default_factory=list, description="Sources or attestations")
    created_date: Optional[datetime] = Field(None, description="When this entry was created")
    last_modified: Optional[datetime] = Field(None, description="When last updated")
    status: Optional[str] = Field(
        None,
        description="Completeness status (draft, partial, complete, verified)"
    )
    
    # Legacy compatibility fields
    tags: Optional[List[str]] = Field(default_factory=list, description="Classification tags")
    cognates: Optional[List[str]] = Field(default_factory=list, description="Cognates in other languages")

# Phoneme model
class Phoneme(GenericEntryModel):
    """A phoneme in a language"""
    symbol: str
    features: Optional[Dict[str, bool]] = Field(default_factory=dict)
    description: Optional[str] = None
    example_words: Optional[List[str]] = Field(default_factory=list)
    ipa: Optional[str] = None
    sound_type: Optional[str] = "consonant"
    articulation: Optional[Dict[str, str]] = Field(default_factory=dict)

# MorphologicalRule model
class MorphologicalRule(GenericEntryModel):
    """A morphological rule in a language"""
    name: str
    description: Optional[str] = None
    pattern: str
    replacement: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    examples: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    rule_type: Optional[str] = "inflection"
    applies_to: Optional[List[str]] = Field(default_factory=list)

# Language model 
class Language(GenericEntryModel):
    """A constructed language"""
    name: str
    code: str
    description: Optional[str] = None
    creator: Optional[str] = None
    creation_date: Optional[datetime] = None
    phonology: Optional[Dict[str, Any]] = Field(default_factory=dict)
    grammar: Optional[Dict[str, Any]] = Field(default_factory=dict)
    vocabulary_size: Optional[int] = 0
    writing_system: Optional[Dict[str, Any]] = None

# Text model
class Text(GenericEntryModel):
    """A text in a constructed language"""
    title: Optional[str] = None
    content: str
    language: str
    translation: Optional[str] = None
    notes: Optional[str] = None
    glosses: Optional[List[Dict[str, str]]] = Field(default_factory=list)

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
            "anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}],
            "description": "Allowed onset consonants"
        },
        "allowed_nuclei": {
            "anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}],
            "description": "Allowed nucleus vowels"
        },
        "allowed_codas": {
            "anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}],
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
            "anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}],
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