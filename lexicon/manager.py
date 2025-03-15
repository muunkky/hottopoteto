from typing import Dict, List, Optional, Union, Any
import os
import json
import uuid
from datetime import datetime
from jsonschema import validate, ValidationError
import logging
import jsonschema

# Change from relative to absolute imports
from lexicon.models.word import WordEntryModel
from lexicon.schema import get_word_schema
from lexicon.indexing import update_indices, load_index, search_by_criteria
from lexicon.migrations import migrate_word
from lexicon.utils import repair_word_entry

# Add a custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class LexiconManager:
    """
    Manages the lexicon as a repository of word entries.
    Handles CRUD operations, indexing, and schema validation.
    """
    
    def __init__(self, lexicon_dir: str = "lexicon"):
        """Initialize the lexicon manager with directory configuration"""
        self.lexicon_dir = lexicon_dir
        # Check if the parent directory is writable
        parent = os.path.dirname(os.path.abspath(lexicon_dir))
        if not os.access(parent, os.W_OK):
            raise Exception(f"Parent directory {parent} is not writable")
            
        self.schema = get_word_schema()
        self.words_dir = os.path.join(lexicon_dir, "words")
        self.indices_dir = os.path.join(lexicon_dir, "indices")
        
        # Create directories if they don't exist
        os.makedirs(self.words_dir, exist_ok=True)
        os.makedirs(self.indices_dir, exist_ok=True)
    
    def add_word(self, word_entry: Union[Dict, WordEntryModel], validate: bool = True) -> str:
        """
        Add a word to the lexicon, performing schema validation.
        Returns the word_id of the added entry.
        """
        # Convert to dict if it's a model
        if isinstance(word_entry, WordEntryModel):
            word_data = word_entry.to_dict()
        else:
            word_data = word_entry.copy()  # Make a copy to avoid modifying the original
            
            # Convert datetime objects in metadata to strings before validation
            if "metadata" in word_data:
                for field in ["created_at", "updated_at"]:
                    if field in word_data["metadata"] and isinstance(word_data["metadata"][field], datetime):
                        word_data["metadata"][field] = word_data["metadata"][field].isoformat()

            # Handle any timestamps in generation_data
            if "generation_data" in word_data and "timestamp" in word_data["generation_data"]:
                if isinstance(word_data["generation_data"]["timestamp"], datetime):
                    word_data["generation_data"]["timestamp"] = word_data["generation_data"]["timestamp"].isoformat()
        
        # Always repair the entry first to fix any issues
        word_data = repair_word_entry(word_data, self.schema)
        
        # Validate against schema if requested
        if validate:
            try:
                jsonschema.validate(instance=word_data, schema=self.schema)
                logging.info(f"Word entry validated successfully against schema")
            except jsonschema.exceptions.ValidationError as e:
                logging.error(f"Word entry failed schema validation: {e}")
                raise ValueError(f"Schema validation failed: {e}")  # Raise ValueError
        
        word_id = word_data["word_id"]
        
        # Save the word file - use the word ID for the filename, not the Eldorian word
        word_file_path = os.path.join(self.words_dir, f"{word_id}.json")
        with open(word_file_path, 'w') as f:
            json.dump(word_data, f, indent=2, cls=DateTimeEncoder)
            
        # Update indices
        update_indices(word_data, self.indices_dir)
        
        return word_id
    
    def get_word(self, word_id_or_name: str) -> Optional[Dict]:
        """
        Retrieve a word by its ID or Eldorian name.
        First tries to find by word_id, then by Eldorian name if not found.
        """
        # Try by word_id first
        word_path = os.path.join(self.words_dir, f"{word_id_or_name}.json")
        
        # If not found, try by Eldorian name
        if not os.path.exists(word_path):
            # Try as an Eldorian name
            word_path = os.path.join(self.words_dir, f"{word_id_or_name.lower()}.json")
            
        if not os.path.exists(word_path):
            return None
            
        try:
            with open(word_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Error loading word {word_id_or_name}: {e}")
    
    def update_word(self, word_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing word entry with new data"""
        current_word = self.get_word(word_id)
        if not current_word:
            return None
            
        # Apply updates
        for key, value in updates.items():
            if key in current_word:
                if isinstance(current_word[key], dict) and isinstance(value, dict):
                    # Deep merge dictionaries
                    current_word[key] = {**current_word[key], **value}
                else:
                    current_word[key] = value
                    
        # Update metadata
        current_word["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Re-validate
        try:
            validate(instance=current_word, schema=self.schema)
        except ValidationError as e:
            raise ValueError(f"Updated word entry failed schema validation: {e}")
            
        # Save the updated word
        word_path = os.path.join(self.words_dir, f"{word_id}.json")
        with open(word_path, 'w') as f:
            json.dump(current_word, f, indent=2, cls=DateTimeEncoder)
            
        # Update indices
        update_indices(current_word, self.indices_dir)
        
        return current_word
    
    def delete_word(self, word_id: str) -> bool:
        """Remove a word from the lexicon"""
        word_path = os.path.join(self.words_dir, f"{word_id}.json")
        if not os.path.exists(word_path):
            return False
            
        # Get the word data to remove from indices
        try:
            with open(word_path, 'r') as f:
                word_data = json.load(f)
                
            # Delete the file
            os.remove(word_path)
            
            # Update indices (remove this word)
            self._remove_from_indices(word_data)
            
            return True
        except Exception as e:
            raise IOError(f"Error deleting word {word_id}: {e}")
    
    def search(self, criteria: Dict) -> List[Dict]:
        """Search for words matching the given criteria"""
        return search_by_criteria(criteria, self.lexicon_dir)
    
    def get_all_words(self) -> List[Dict]:
        """Get all words in the lexicon"""
        results = []
        for filename in os.listdir(self.words_dir):
            if filename.endswith('.json'):
                word_path = os.path.join(self.words_dir, filename)
                try:
                    with open(word_path, 'r') as f:
                        word_data = json.load(f)
                        results.append(word_data)
                except:
                    pass
        return results
    
    def migrate_schema(self, target_version: str) -> int:
        """Migrate all words to a new schema version"""
        migrated_count = 0
        for word_id in self._get_all_word_ids():
            word_data = self.get_word(word_id)
            if word_data:
                current_version = word_data.get("metadata", {}).get("schema_version")
                if current_version != target_version:
                    migrated = migrate_word(word_data, target_version)
                    self.update_word(word_id, migrated)
                    migrated_count += 1
        return migrated_count
    
    def _get_all_word_ids(self) -> List[str]:
        """Get all word IDs in the lexicon"""
        word_ids = []
        for filename in os.listdir(self.words_dir):
            if filename.endswith('.json'):
                word_id = filename.replace('.json', '')
                word_ids.append(word_id)
        return word_ids
    
    def _remove_from_indices(self, word_data: Dict) -> None:
        """Remove a word from all indices"""
        # Implementation depends on how indices are stored
        pass

    def create_word_from_recipe(self, recipe_output: Dict) -> str:
        """Create a word entry from recipe output and add it to the lexicon"""
        word_entry = WordEntryModel.from_recipe_output(recipe_output)
        return self.add_word(word_entry)

    def add_word_from_recipe(self, recipe_output: Dict[str, Any]) -> str:
        """
        Process recipe output into a word entry and add it to the lexicon.
        
        Args:
            recipe_output: The output from a recipe execution
            
        Returns:
            str: The ID of the added word
        """
        # Change from relative to absolute import
        from domains.conlang import ConlangProcessor
        
        # Process recipe output into a word entry
        processor = ConlangProcessor()
        word_entry = processor.process_recipe_output(recipe_output)
        
        # Add the processed word entry to the lexicon
        return self.add_word(word_entry.dict())