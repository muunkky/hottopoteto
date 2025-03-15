import os
import pytest
import json
from typing import Dict, Any

from lexicon.manager import LexiconManager
from core.executor import RecipeExecutor

@pytest.fixture
def temp_lexicon_dir(tmpdir):
    """Create a temporary lexicon directory for testing."""
    lexicon_dir = os.path.join(tmpdir, "temp_lexicon")
    os.makedirs(lexicon_dir, exist_ok=True)
    yield lexicon_dir
    import shutil
    shutil.rmtree(lexicon_dir, ignore_errors=True)

@pytest.fixture
def mock_recipe_output() -> Dict[str, Any]:
    """Create a mock recipe output for testing."""
    class MockDataContainer:
        def __init__(self, data):
            self.data = data
        
        def get_data(self, fallback_to_raw=True):
            return self.data
            
        def get(self, key, default=None):
            return self.data.get(key, default) if isinstance(self.data, dict) else default

    return {
        "Initial_User_Inputs": MockDataContainer({
            "data": {  # Add the data field to match expected structure
                "english_word": "river",
                "part_of_speech": "noun",
                "base_form": "river"
            }
        }),
        "Apply_Phonology": MockDataContainer({
            "data": {  # Add the data field to match expected structure
                "updated_word": "valar",
                "syllables": ["va", "lar"]
            }
        }),
        "Generate_the_Origin_Words": MockDataContainer({
            "data": {  # Add the data field to match expected structure
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
        })
    }

def test_create_word_from_recipe(temp_lexicon_dir, mock_recipe_output):
    """Test creating a word from recipe output."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    
    # Create word from recipe output
    word_id = manager.create_word_from_recipe(mock_recipe_output)
    
    # Verify word was created
    assert word_id is not None
    
    # The file should be stored using the word_id name
    word_file = os.path.join(manager.words_dir, f"{word_id}.json")
    assert os.path.exists(word_file)
    
    # Retrieve the word and check its properties
    word_data = manager.get_word(word_id)
    assert word_data is not None
    assert word_data["eldorian"] == "valar"
    assert word_data["english"] == "river"

@pytest.mark.skip(reason="Requires real LLM API calls")
def test_full_recipe_to_word_flow(temp_lexicon_dir):
    """
    Test the full flow from recipe execution to word creation.
    This test is skipped by default as it requires real LLM API calls.
    """
    # Path to a test recipe
    recipe_path = "recipes/conlang/test_recipe.yaml"
    
    # Create and execute recipe
    executor = RecipeExecutor(recipe_path=recipe_path)
    recipe_output = executor.execute(inputs={
        "english_word": "river",
        "connotation": "flowing body of water"
    })
    
    # Create word from recipe output
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_id = manager.create_word_from_recipe(recipe_output)
    
    # Verify word was created correctly
    assert word_id is not None
    word_data = manager.get_word(word_id)
    assert word_data is not None
    assert "river" in word_data["english"]
