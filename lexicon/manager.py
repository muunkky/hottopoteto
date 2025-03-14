from typing import Dict, List, Optional, Union, Any
import os
import json
import uuid
from datetime import datetime
from jsonschema import validate, ValidationError
import logging
import jsonschema

from .models.word import WordEntryModel
from .schema import get_word_schema
from .indexing import update_indices, load_index, search_by_criteria
from .migrations import migrate_word
from .utils import repair_word_entry

class LexiconManager:
    """
    Manages the lexicon as a repository of word entries.
    Handles CRUD operations, indexing, and schema validation.
    """
    
    def __init__(self, lexicon_dir: str = "lexicon"):
        """Initialize the lexicon manager with directory configuration"""
        self.lexicon_dir = lexicon_dir
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
            word_data = word_entry
        
        # Validate against schema if requested
        if validate:
            try:
                jsonschema.validate(instance=word_data, schema=self.schema)
                logging.info(f"Word entry validated successfully against schema")
            except jsonschema.exceptions.ValidationError as e:
                logging.error(f"Word entry failed schema validation: {e}")
                # Fix the entry automatically
                word_data = repair_word_entry(word_data, self.schema)
        
        word_id = word_data["word_id"]
        
        # Save the word file
        word_file_path = os.path.join(self.words_dir, f"{word_data['eldorian'].lower()}.json")
        with open(word_file_path, 'w') as f:
            json.dump(word_data, f, indent=2)
            
        # Update indices
        update_indices(word_data, self.indices_dir)
        
        return word_id
    
    def get_word(self, word_id: str) -> Optional[Dict]:
        """Retrieve a word by its ID"""
        word_path = os.path.join(self.words_dir, f"{word_id}.json")
        if not os.path.exists(word_path):
            return None
            
        try:
            with open(word_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Error loading word {word_id}: {e}")
    
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
            json.dump(current_word, f, indent=2)
            
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
        from ..domains.conlang import ConlangProcessor
        
        # Process recipe output into a word entry
        processor = ConlangProcessor()
        word_entry = processor.process_recipe_output(recipe_output)
        
        # Add the processed word entry to the lexicon
        return self.add_word(word_entry.dict())