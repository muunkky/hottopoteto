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
            "$type": "NounProperties",
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

def test_add_word_invalid_schema(temp_lexicon_dir):
    """Test adding a word with an invalid schema."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    word_entry = create_sample_word_entry()
    del word_entry["eldorian"]  # Remove a required field
    with pytest.raises(ValueError):  # Expect a ValueError due to empty required field
        manager.add_word(word_entry)  # Use default validate=True

def test_get_word_not_found(temp_lexicon_dir):
    """Test getting a word that doesn't exist."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    retrieved_word = manager.get_word("nonexistent-word")
    assert retrieved_word is None

def test_update_word_not_found(temp_lexicon_dir):
    """Test updating a word that doesn't exist."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    updates = {"english": "updated test word"}
    updated_word = manager.update_word("nonexistent-word", updates)
    assert updated_word is None

def test_delete_word_not_found(temp_lexicon_dir):
    """Test deleting a word that doesn't exist."""
    manager = LexiconManager(lexicon_dir=temp_lexicon_dir)
    result = manager.delete_word("nonexistent-word")
    assert result is False

def test_lexicon_manager_invalid_dir(monkeypatch):
    """Test initializing LexiconManager with an invalid directory."""
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    with pytest.raises(Exception):
        LexiconManager(lexicon_dir="C:\\NonWritableDir\\lexicon")
