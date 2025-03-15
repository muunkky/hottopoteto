import pytest
from datetime import datetime
from typing import Dict, Any

from lexicon.models.word import WordEntryModel
from core.executor import RecipeLinkOutput  # Import from core.executor instead of creating a mock

def create_sample_recipe_output() -> Dict[str, Any]:
    """Create a sample recipe output for testing."""
    # Create a structure that mimics the actual RecipeLinkOutput objects
    class MockDataContainer:
        def __init__(self, data):
            self.data = data
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def get_data(self, fallback_to_raw=True):
            return self.data

    return {
        "Initial_User_Inputs": MockDataContainer({
            "data": {
                "english_word": "river",
                "part_of_speech": "noun",
                "base_form": "river"
            }
        }),
        "Apply_Phonology": MockDataContainer({
            "data": {
                "updated_word": "valar",
                "syllables": ["va", "lar"]
            }
        }),
        "Generate_the_Origin_Words": MockDataContainer({
            "data": {
                "revised_connotation": "flowing body of water",
                "origin_words": [
                    {
                        "word": "val",
                        "language": "Old Elven",
                        "meaning": "flowing"
                    },
                    {
                        "word": "ar",
                        "language": "Old Elven",
                        "meaning": "water"
                    }
                ]
            }
        }),
        "Pronunciation": MockDataContainer({
            "data": {
                "ipa": "/valaɾ/",
                "stress_pattern": "10"
            }
        })
    }

def test_from_recipe_output_basic():
    """Test basic conversion from recipe output to WordEntryModel."""
    recipe_output = create_sample_recipe_output()
    word_entry = WordEntryModel.from_recipe_output(recipe_output)
    
    # Check basic properties
    assert word_entry.eldorian == "valar"
    assert word_entry.english == "river"
    assert "noun" in word_entry.core.get("part_of_speech", "")
    
    # Check generated ID follows expected pattern
    assert word_entry.id.startswith("valar-")
    
    # Check metadata
    assert word_entry.metadata["schema_version"] == "1.0"
    
def test_from_recipe_output_etymology():
    """Test that etymology data is correctly extracted."""
    recipe_output = create_sample_recipe_output()
    word_entry = WordEntryModel.from_recipe_output(recipe_output)
    
    # Check etymology section
    etymology = word_entry.etymology
    assert len(etymology.get("origin_words", [])) == 2
    assert etymology["origin_words"][0]["word"] == "val"
    assert etymology["origin_words"][1]["meaning"] == "water"
    
def test_from_recipe_output_pronunciation():
    """Test that pronunciation data is correctly extracted."""
    recipe_output = create_sample_recipe_output()
    word_entry = WordEntryModel.from_recipe_output(recipe_output)
    
    # Check pronunciation
    pronunciation = word_entry.core.get("pronunciation", {})
    assert pronunciation.get("ipa") == "/valaɾ/"
    
def test_from_recipe_output_grammatical_properties():
    """Test that grammatical properties are correctly set based on part of speech."""
    recipe_output = create_sample_recipe_output()
    word_entry = WordEntryModel.from_recipe_output(recipe_output)
    
    # For a noun, we should have noun properties
    assert word_entry.grammatical_properties.type == "NounProperties"
    assert hasattr(word_entry.grammatical_properties, "gender")

def test_from_recipe_output_missing_required_field():
    """Test from_recipe_output with a missing required field in the recipe output."""
    # Create a mock recipe output missing "Initial_User_Inputs"
    class MockDataContainer:
        def __init__(self, data):
            self.data = data
        def get(self, key, default=None):
            return self.data.get(key, default)
        def get_data(self, fallback_to_raw=True):
            return self.data
    recipe_output = {
        "Apply_Phonology": MockDataContainer({
            "data": {             # Added nested "data" key
                "updated_word": "valar",
                "syllables": ["va", "lar"]
            }
        }),
        "Generate_the_Origin_Words": MockDataContainer({
            "data": {
                "revised_connotation": "flowing body of water",
                "origin_words": []
            }
        })
        # "Initial_User_Inputs" is omitted
    }
    # The missing field will default to "unknown"
    word_entry = WordEntryModel.from_recipe_output(recipe_output)
    assert word_entry.english == "unknown"
    # and eldorian becomes from phonology ("valar")
    assert word_entry.eldorian == "valar"

def test_from_recipe_output_invalid_data_type():
    """Test from_recipe_output with invalid data types in the recipe output."""
    # Provide an invalid type for 'Initial_User_Inputs' (integer instead of expected object)
    class MockDataContainer:
        def __init__(self, data):
            self.data = data
        def get(self, key, default=None):
            return self.data.get(key, default)
        def get_data(self, fallback_to_raw=True):
            return self.data
    recipe_output = {
        "Initial_User_Inputs": 123,  # Invalid type: should support get() and get_data()
        "Apply_Phonology": MockDataContainer({
            "data": {
                "updated_word": "valar",
                "syllables": ["va", "lar"]
            }
        }),
        "Generate_the_Origin_Words": MockDataContainer({
            "data": {
                "revised_connotation": "flowing body of water",
                "origin_words": []
            }
        })
    }
    with pytest.raises(AttributeError):
        # Calling .get on an integer will raise AttributeError.
        WordEntryModel.from_recipe_output(recipe_output)
