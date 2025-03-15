import os
import json
import pytest
import shutil
from lexicon.indexing import update_indices, load_index, save_index, search_by_criteria

# Fixture: temporary lexicon directory with "words" and "indices" folders
@pytest.fixture
def temp_lexicon_dir(tmpdir):
    lexicon_dir = os.path.join(tmpdir, "lexicon")
    words_dir = os.path.join(lexicon_dir, "words")
    indices_dir = os.path.join(lexicon_dir, "indices")
    os.makedirs(words_dir, exist_ok=True)
    os.makedirs(indices_dir, exist_ok=True)
    yield lexicon_dir
    shutil.rmtree(lexicon_dir, ignore_errors=True)

# Fixture: sample word entries for testing indices and search functions
@pytest.fixture
def sample_word_entries():
    entry1 = {
        "word_id": "word-001",
        "english": "TestWord",
        "eldorian": "testword",
        "core": {
            "part_of_speech": "noun",
            "pronunciation": {"ipa": "/tɛstwɜːrd/"},
            "syllables": ["test", "word"],
            "definitions": [{"meaning": "a test word", "domain": "general", "register": "standard", "examples": []}]
        },
        "grammatical_properties": {
            "$type": "NounProperties",
            "gender": "neutral",
            "countability": "countable",
            "declension_class": "regular",
            "case_forms": {"nominative": {"singular": "testword", "plural": "testwords"}}
        },
        "etymology": {"origin_words": [{"language": "Old Elven", "word": "val", "meaning": "flowing"}]},
        "relationships": {"derivatives": [], "synonyms": [], "antonyms": [], "morphological": [],
                          "semantic": [], "etymological": []},
        "homonyms": [],
        "metadata": {"schema_version": "1.0", "created_at": "2023-01-01T00:00:00", "updated_at": "2023-01-01T00:00:00",
                     "recipe_id": "eldorian_word_v1", "tags": []},
        "generation_data": {}
    }
    entry2 = {
        "word_id": "word-002",
        "english": "Run",
        "eldorian": "run",
        "core": {
            "part_of_speech": "verb",
            "pronunciation": {"ipa": "/rʌn/"},
            "syllables": ["run"],
            "definitions": [{"meaning": "to run", "domain": "action", "register": "standard", "examples": []}]
        },
        "grammatical_properties": {
            "$type": "VerbProperties",
            "transitivity": "intransitive",
            "conjugation_class": "regular",
            "tense_forms": {"present": {"first_singular": "run"}},
            "infinitive": "run"
        },
        "etymology": {"origin_words": []},
        "relationships": {"derivatives": [], "synonyms": [], "antonyms": [], "morphological": [],
                          "semantic": [], "etymological": []},
        "homonyms": [],
        "metadata": {"schema_version": "1.0", "created_at": "2023-01-02T00:00:00", "updated_at": "2023-01-02T00:00:00",
                     "recipe_id": "eldorian_word_v1", "tags": []},
        "generation_data": {}
    }
    entry3 = {
        "word_id": "word-003",
        "english": "Apple",
        "eldorian": "apple",
        "core": {
            "part_of_speech": "noun",
            "pronunciation": {"ipa": "/ˈæpəl/"},
            "syllables": ["ap", "ple"],
            "definitions": [{"meaning": "a fruit", "domain": "food", "register": "standard", "examples": []}]
        },
        "grammatical_properties": {
            "$type": "NounProperties",
            "gender": "neutral",
            "countability": "uncountable",
            "declension_class": "regular",
            "case_forms": {"nominative": {"singular": "apple", "plural": "apples"}}
        },
        "etymology": {"origin_words": [{"language": "Modern Elven", "word": "appel", "meaning": "fruit"}]},
        "relationships": {"derivatives": [], "synonyms": [], "antonyms": [], "morphological": [],
                          "semantic": [], "etymological": []},
        "homonyms": [],
        "metadata": {"schema_version": "1.0", "created_at": "2023-01-03T00:00:00", "updated_at": "2023-01-03T00:00:00",
                     "recipe_id": "eldorian_word_v1", "tags": []},
        "generation_data": {}
    }
    return [entry1, entry2, entry3]

def test_update_indices(temp_lexicon_dir, sample_word_entries):
    """Test update_indices with different types of word entries."""
    indices_dir = os.path.join(temp_lexicon_dir, "indices")
    os.makedirs(indices_dir, exist_ok=True)
    
    # Clear any existing index files
    for fname in ["by_english.json", "by_part_of_speech.json", "by_origin_language.json", "by_semantic_domain.json"]:
        path = os.path.join(indices_dir, fname)
        if os.path.exists(path):
            os.remove(path)
    
    # Update indices with each sample word
    for entry in sample_word_entries:
        update_indices(entry, indices_dir)
    
    # Load and verify the English index
    english_index = load_index(os.path.join(indices_dir, "by_english.json"))
    # Entry1 english "testword" -> lowercase "testword"
    assert "testword" in english_index
    assert sample_word_entries[0]["word_id"] in english_index["testword"]
    # Entry2 english "Run" -> "run"
    assert "run" in english_index
    assert sample_word_entries[1]["word_id"] in english_index["run"]
    
    # Verify part of speech index
    pos_index = load_index(os.path.join(indices_dir, "by_part_of_speech.json"))
    assert "noun" in pos_index
    assert sample_word_entries[0]["word_id"] in pos_index["noun"]
    # Entry2 is a verb
    assert "verb" in pos_index
    assert sample_word_entries[1]["word_id"] in pos_index["verb"]
    
    # Verify origin language index
    origin_index = load_index(os.path.join(indices_dir, "by_origin_language.json"))
    # Entry1 has origin language "Old Elven"
    assert "Old Elven" in origin_index
    assert sample_word_entries[0]["word_id"] in origin_index["Old Elven"]
    # Entry3 has origin language "Modern Elven"
    assert "Modern Elven" in origin_index
    assert sample_word_entries[2]["word_id"] in origin_index["Modern Elven"]
    
    # Verify semantic domain index from definitions in core
    domain_index = load_index(os.path.join(indices_dir, "by_semantic_domain.json"))
    # Entry1 "general"; Entry2 "action"; Entry3 "food"
    assert "general" in domain_index
    assert sample_word_entries[0]["word_id"] in domain_index["general"]
    assert "action" in domain_index
    assert sample_word_entries[1]["word_id"] in domain_index["action"]
    assert "food" in domain_index
    assert sample_word_entries[2]["word_id"] in domain_index["food"]

def test_search_by_criteria_found(temp_lexicon_dir, sample_word_entries):
    """Test search_by_criteria with different criteria combinations."""
    # Setup: Create words directory and write each word as JSON file
    words_dir = os.path.join(temp_lexicon_dir, "words")
    indices_dir = os.path.join(temp_lexicon_dir, "indices")
    os.makedirs(words_dir, exist_ok=True)
    os.makedirs(indices_dir, exist_ok=True)
    
    # Write each word entry into words folder
    for entry in sample_word_entries:
        path = os.path.join(words_dir, f"{entry['word_id']}.json")
        with open(path, 'w') as f:
            json.dump(entry, f)
        # Also update indices
        update_indices(entry, indices_dir)
    
    # Criteria 1: Search by english_contains "run"
    results = search_by_criteria({"english_contains": "run"}, temp_lexicon_dir)
    assert len(results) == 1
    assert results[0]["word_id"] == "word-002"
    
    # Criteria 2: Search by part_of_speech "noun"
    results = search_by_criteria({"part_of_speech": "noun"}, temp_lexicon_dir)
    # Expect two results: entry1 and entry3
    result_ids = {r["word_id"] for r in results}
    assert "word-001" in result_ids
    assert "word-003" in result_ids
    
    # Criteria 3: Search by origin_language "Old Elven"
    results = search_by_criteria({"origin_language": "Old Elven"}, temp_lexicon_dir)
    assert len(results) == 1
    assert results[0]["word_id"] == "word-001"
    
    # Combine criteria: english_contains "apple" and part_of_speech "noun"
    results = search_by_criteria({"english_contains": "apple", "part_of_speech": "noun"}, temp_lexicon_dir)
    assert len(results) == 1
    assert results[0]["word_id"] == "word-003"

def test_search_by_criteria_none(temp_lexicon_dir, sample_word_entries):
    """Test search_by_criteria with no matching words."""
    # Setup: Create words and indices inside lexicon_dir
    words_dir = os.path.join(temp_lexicon_dir, "words")
    indices_dir = os.path.join(temp_lexicon_dir, "indices")
    os.makedirs(words_dir, exist_ok=True)
    os.makedirs(indices_dir, exist_ok=True)
    
    # Write each entry into words folder and update indices
    for entry in sample_word_entries:
        path = os.path.join(words_dir, f"{entry['word_id']}.json")
        with open(path, 'w') as f:
            json.dump(entry, f)
        update_indices(entry, indices_dir)
    
    # Search criteria with no match: english_contains "nonexistent"
    results = search_by_criteria({"english_contains": "nonexistent"}, temp_lexicon_dir)
    assert results == []
    
    # Another criteria: part_of_speech "adverb" (none of our entries are adverbs)
    results = search_by_criteria({"part_of_speech": "adverb"}, temp_lexicon_dir)
    assert results == []
