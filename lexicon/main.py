# Using the refactored code

from lexicon.manager import LexiconManager
from lexicon.models.word import WordEntryModel

# Initialize the lexicon manager
lexicon = LexiconManager(lexicon_dir="lexicon")

# Get all words in the lexicon
all_words = lexicon.get_all_words()
print(f"Lexicon contains {len(all_words)} words")

# Search for words
elven_words = lexicon.search({
    "origin_language": "Old Elven",
    "part_of_speech": "noun"
})
print(f"Found {len(elven_words)} Old Elven nouns")

# Add a new word from recipe output
recipe_output = {
    "Apply_Phonology": {"data": {"updated_word": "velaris"}},
    "Initial_User_Inputs": {"data": {"english_word": "star", "part_of_speech": "noun"}}
}
new_word_id = lexicon.create_word_from_recipe(recipe_output)
print(f"Added new word with ID: {new_word_id}")

# Update a word
lexicon.update_word(new_word_id, {
    "relationships": {
        "synonyms": ["silanthor"]
    }
})

# Migrate all words to a new schema version
migrated_count = lexicon.migrate_schema("1.1")
print(f"Migrated {migrated_count} words to schema v1.1")