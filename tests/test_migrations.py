import pytest
from datetime import datetime
from lexicon.migrations import migrate_word

@pytest.fixture
def sample_word_v10():
    """Return a sample word entry with schema version 1.0."""
    return {
        "word_id": "word-001",
        "eldorian": "valar",
        "english": "river",
        "core": {
            "part_of_speech": "noun",
            "pronunciation": {"ipa": "/valaɾ/"},
            "syllables": ["va", "lar"],
            "definitions": [{
                "meaning": "a river",
                "domain": "general",
                "register": "standard",
                "examples": []
            }]
        },
        "grammatical_properties": {
            "$type": "NounProperties",
            "gender": "neutral",
            "countability": "countable",
            "declension_class": "regular",
            "case_forms": {"nominative": {"singular": "valar", "plural": ""}}
        },
        "etymology": {"origin_words": []},
        "relationships": {
            "derivatives": [],
            "synonyms": [],
            "antonyms": [],
            "morphological": [],
            "semantic": [],
            "etymological": []
        },
        "homonyms": [],
        "metadata": {
            "schema_version": "1.0",
            "created_at": datetime(2023, 1, 1).isoformat()
        },
        "generation_data": {}
    }

def test_migrate_word_from_v10_to_latest(sample_word_v10):
    """Test migrating a word from v1.0 to the latest version (1.2)."""
    migrated = migrate_word(sample_word_v10, "1.2")
    # Check that metadata schema_version was updated to 1.2.
    assert migrated["metadata"]["schema_version"] == "1.2"
    # Check that migration for v1.0->v1.1 added usage_examples.
    assert "usage_examples" in migrated
    # Check that migration for v1.1->v1.2 added cultural_notes.
    assert "cultural_notes" in migrated
    # Verify that updated_at exists.
    assert "updated_at" in migrated["metadata"]

def test_migrate_word_already_latest(sample_word_v10):
    """Test migrating a word that is already at the latest version; should remain unchanged."""
    migrated = migrate_word(sample_word_v10, "1.2")
    migrated_again = migrate_word(migrated, "1.2")
    assert migrated == migrated_again

def test_migrate_word_missing_fields():
    """Test migrating a word with missing required fields (e.g. missing metadata, core)."""
    word = {
        "word_id": "word-002",
        "eldorian": "run",
        "english": "run",
        # Missing core and metadata.
        "grammatical_properties": {},
        "etymology": {},
        "relationships": {},
        "homonyms": [],
        "generation_data": {}
    }
    # Without metadata, the default version will be assumed as "1.0".
    migrated = migrate_word(word, "1.1")
    # Check that metadata was added and schema_version updated.
    assert "metadata" in migrated
    assert migrated["metadata"]["schema_version"] == "1.1"
    # Check that created_at is present in metadata.
    assert "created_at" in migrated["metadata"]
