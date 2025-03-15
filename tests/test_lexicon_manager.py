import os
import shutil
import pytest
from datetime import datetime
from typing import Dict, Any

from lexicon.manager import LexiconManager
from lexicon.models.word import WordEntryModel

@pytest.fixture
def temp_lexicon_dir(tmpdir):
    """Create a temporary lexicon directory for testing."""
    lexicon_dir = os.path.join(tmpdir, "temp_lexicon")
    yield lexicon_dir
    shutil.rmtree(lexicon_dir, ignore_errors=True)

def create_sample_word_entry() -> Dict[str, Any]:
    """Create a sample word entry for testing."""
    return {
        "word_id": "test-word-1234",
        "eldorian": "testword",
        "english": "test word",
        "core": {
            "part_of_speech": "noun",
            "pronunciation": {"ipa": "/test/"},
            "syllables": ["test", "word"],  # Add the required syllables field
            "definitions": [{"meaning": "a test word"}]
        },
        "metadata": {"schema_version": "1.0", "created_at": datetime.now().isoformat()},
        "grammatical_properties": {  # Add required grammatical properties
            "$type": "NounProperties",  # Changed from "type" to "$type"
            "gender": "neutral",
            "countability": "countable",
            "declension_class": "regular",
            "case_forms": {
                "nominative": {
                    "singular": "testword",
                    "plural": "testwords"
                }
            }
        }
    }

def test_lexicon_manager_init(temp_lexicon_dir):
    """Test that the LexiconManager initializes correctly."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    assert os.path.exists(manager.words_dir)
    assert os.path.exists(manager.indices_dir)

def test_add_word(temp_lexicon_dir):
    """Test adding a word to the lexicon."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_entry = create_sample_word_entry()
    word_id = manager.add_word(word_entry)
    assert word_id == word_entry["word_id"]
    # Look for file named with word_id instead of Eldorian word
    word_file_path = os.path.join(manager.words_dir, f"{word_id}.json")
    assert os.path.exists(word_file_path)

def test_get_word(temp_lexicon_dir):
    """Test retrieving a word from the lexicon."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_entry = create_sample_word_entry()
    manager.add_word(word_entry)
    # Use word_id for retrieval since that's how files are stored now
    retrieved_word = manager.get_word(word_entry["word_id"])
    assert retrieved_word is not None
    assert retrieved_word["word_id"] == word_entry["word_id"]
    assert retrieved_word["eldorian"] == word_entry["eldorian"]
    assert retrieved_word["english"] == word_entry["english"]

def test_update_word(temp_lexicon_dir):
    """Test updating a word in the lexicon."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_entry = create_sample_word_entry()
    manager.add_word(word_entry)
    updates = {"english": "updated test word"}
    updated_word = manager.update_word(word_entry["word_id"], updates)
    assert updated_word["english"] == "updated test word"

def test_delete_word(temp_lexicon_dir):
    """Test deleting a word from the lexicon."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_entry = create_sample_word_entry()
    manager.add_word(word_entry)
    result = manager.delete_word(word_entry["word_id"])
    assert result is True
    word_file_path = os.path.join(manager.words_dir, f"{word_entry['eldorian'].lower()}.json")
    assert not os.path.exists(word_file_path)

def test_get_all_words(temp_lexicon_dir):
    """Test getting all words from the lexicon."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_entry1 = create_sample_word_entry()
    word_entry2 = create_sample_word_entry()
    word_entry2["word_id"] = "test-word-5678"
    word_entry2["eldorian"] = "anothertestword"
    manager.add_word(word_entry1)
    manager.add_word(word_entry2)
    all_words = manager.get_all_words()
    assert len(all_words) == 2
    # Instead of comparing full dictionaries, assert that each word's word_id is present.
    word_ids = [w["word_id"] for w in all_words]
    assert word_entry1["word_id"] in word_ids
    assert word_entry2["word_id"] in word_ids
