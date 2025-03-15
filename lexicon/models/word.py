from datetime import datetime
from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel, Field

from core.models import GenericEntryModel
from lexicon.utils import generate_word_id

class PronunciationModel(BaseModel):
    ipa: str = ""
    stress_pattern: str = ""
    audio_file: Optional[str] = None

class DefinitionModel(BaseModel):
    meaning: str
    domain: str = "general"
    register: str = "standard"
    examples: List[str] = Field(default_factory=list)

class OriginWordModel(BaseModel):
    word: str
    language: str
    meaning: str

class RelationshipModel(BaseModel):
    type: str
    target_id: str
    properties: Dict = Field(default_factory=dict)

class NounPropertiesModel(BaseModel):
    type: Literal["NounProperties"] = "NounProperties"
    type_field: str = Field("NounProperties", alias="$type")  # Changed from __type to type_field
    gender: str = "neutral"
    countability: str = "countable"
    declension_class: str = "regular"
    case_forms: Dict = Field(default_factory=dict)

class VerbPropertiesModel(BaseModel):
    type: Literal["VerbProperties"] = "VerbProperties"
    type_field: str = Field("VerbProperties", alias="$type")  # Changed from __type to type_field
    transitivity: str = "intransitive"
    conjugation_class: str = "regular"
    tense_forms: Dict = Field(default_factory=dict)
    infinitive: str = ""

class AdjectivePropertiesModel(BaseModel):
    type: Literal["AdjectiveProperties"] = "AdjectiveProperties"
    type_field: str = Field("AdjectiveProperties", alias="$type")  # Changed from __type to type_field
    comparison: Dict = Field(default_factory=dict)
    agreement_forms: Dict = Field(default_factory=dict)

class MetadataModel(BaseModel):
    schema_version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    recipe_id: str = "eldorian_word_v1"
    tags: List[str] = Field(default_factory=list)

# Update WordEntryModel to inherit from GenericEntryModel
class WordEntryModel(GenericEntryModel):
    """Model for a word entry in the lexicon."""
    eldorian: str
    english: str
    core: Dict[str, Any] = Field(default_factory=dict)
    grammatical_properties: Union[NounPropertiesModel, VerbPropertiesModel, AdjectivePropertiesModel, Dict[str, Any]]
    etymology: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, List[RelationshipModel]] = Field(default_factory=dict)
    usage_examples: List[str] = Field(default_factory=list)
    homonyms: List[str] = Field(default_factory=list)
    cultural_notes: List[str] = Field(default_factory=list)
    generation_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Override GenericEntryModel's fields to customize them for words
    id: str = Field(alias="word_id")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with proper field mapping."""
        data = self.model_dump(by_alias=True)
        # Ensure id is properly mapped to word_id
        if "id" in data and "word_id" not in data:
            data["word_id"] = data.pop("id")
            
        # Convert datetime objects to ISO format strings
        if "metadata" in data:
            for field in ["created_at", "updated_at"]:
                if field in data["metadata"] and isinstance(data["metadata"][field], datetime):
                    data["metadata"][field] = data["metadata"][field].isoformat()
                    
        # Handle any timestamps in generation_data
        if "generation_data" in data and "timestamp" in data["generation_data"]:
            if isinstance(data["generation_data"]["timestamp"], datetime):
                data["generation_data"]["timestamp"] = data["generation_data"]["timestamp"].isoformat()
                
        return data
        
    # Keep the from_recipe_output method
    @classmethod
    def from_recipe_output(cls, recipe_output: Dict) -> 'WordEntryModel':
        """Create a WordEntryModel from recipe output."""
        # Extract base information from recipe output
        apply_phonology = recipe_output.get("Apply_Phonology", {})
        initial_inputs = recipe_output.get("Initial_User_Inputs", {})
        
        # Raise error if Initial_User_Inputs is not a dict-like object
        if not hasattr(initial_inputs, 'get'):
            raise AttributeError("Invalid type for Initial_User_Inputs: expected an object with a get() method.")
        
        # Safely extract data with proper fallbacks
        phonology_data = apply_phonology.get("data", {}) if hasattr(apply_phonology, 'get') else {}
        input_data = initial_inputs.get("data", {}) if hasattr(initial_inputs, 'get') else {}
        
        # Basic word properties
        eldorian_word = phonology_data.get("updated_word", "unknown")
        english_word = input_data.get("english_word", "unknown")
        part_of_speech = input_data.get("part_of_speech", "unknown")
        
        # Generate a consistent ID
        word_id = generate_word_id(eldorian_word)
        
        # Extract etymological data
        origin_data = {}
        if "Generate_the_Origin_Words" in recipe_output:
            origin_link = recipe_output["Generate_the_Origin_Words"]
            if hasattr(origin_link, 'data'):
                origin_data = origin_link.data.get("data", {})
            elif hasattr(origin_link, 'get'):
                origin_data = origin_link.get("data", {})
        
        origin_words = origin_data.get("origin_words", [])
        
        # Extract pronunciation
        pronunciation = {}
        if "Pronunciation" in recipe_output:
            pron_link = recipe_output["Pronunciation"]
            if hasattr(pron_link, 'get_data'):
                pron_data = pron_link.data.get("data", {})
            elif hasattr(pron_link, 'get'):
                pron_data = pron_link.get("data", {})
            pronunciation = {
                "ipa": pron_data.get("ipa", ""),
                "stress_pattern": pron_data.get("stress_pattern", "")
            }
        
        # Determine which grammatical properties model to use
        grammar_model_class = None
        if part_of_speech == "noun":
            grammar_model_class = NounPropertiesModel
        elif part_of_speech == "verb":
            grammar_model_class = VerbPropertiesModel
        elif part_of_speech == "adjective":
            grammar_model_class = AdjectivePropertiesModel
        else:
            # Default to noun for unknown parts of speech
            grammar_model_class = NounPropertiesModel
        
        # Create grammatical properties based on part of speech
        grammar_props = {}
        if part_of_speech == "noun":
            grammar_props = {
                "$type": "NounProperties",
                "gender": "neutral",
                "countability": "countable",
                "declension_class": "regular",
                "case_forms": {
                    "nominative": {
                        "singular": eldorian_word,
                        "plural": ""
                    }
                }
            }
        elif part_of_speech == "verb":
            grammar_props = {
                "$type": "VerbProperties",
                "transitivity": "intransitive",
                "conjugation_class": "regular",
                "tense_forms": {
                    "present": {
                        "first_singular": eldorian_word
                    }
                },
                "infinitive": ""
            }
        elif part_of_speech == "adjective":
            grammar_props = {
                "$type": "AdjectiveProperties",
                "comparison": {
                    "comparative": "",
                    "superlative": ""
                },
                "agreement_forms": {
                    "masculine": "",
                    "feminine": "",
                    "neuter": eldorian_word,
                    "plural": ""
                }
            }
        
        # Create the grammatical properties instance
        grammatical_properties = grammar_model_class(**grammar_props)
        
        # Create metadata model but don't convert to dict
        metadata_obj = MetadataModel(
            schema_version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            recipe_id="eldorian_word_v1",
            tags=[]
        )
        
        # Convert the MetadataModel to a dictionary
        metadata_dict = metadata_obj.model_dump()

        # Build all the required data for the WordEntryModel
        return cls(
            word_id=word_id,
            eldorian=eldorian_word,
            english=english_word,
            core={
                "part_of_speech": part_of_speech,
                "pronunciation": pronunciation,
                "syllables": phonology_data.get("syllables", []),
                "connotation": origin_data.get("revised_connotation", ""),
                "definitions": [
                    {
                        "meaning": english_word,
                        "domain": origin_data.get("semantic_domain", "general"),
                        "register": origin_data.get("register", "standard"),
                        "examples": []
                    }
                ]
            },
            grammatical_properties=grammatical_properties,
            etymology={
                "origin_words": [
                    {
                        "word": origin.get("word", ""),
                        "language": origin.get("language", ""),
                        "meaning": origin.get("meaning", "")
                    }
                    for origin in origin_words
                ]
            },
            relationships={
                "derivatives": [],
                "synonyms": [],
                "antonyms": [],
                "morphological": [],
                "semantic": [],
                "etymological": []
            },
            homonyms=[],
            metadata=metadata_dict,  # Pass the dictionary to the model
            generation_data={
                "source": "recipe",
                "timestamp": datetime.now().isoformat()
            }
        )