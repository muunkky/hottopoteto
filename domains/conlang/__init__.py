"""
Conlang domain module for processing constructed language data.
"""
from typing import Dict, Any, List, Optional
import os

from .. import DomainProcessor, register_domain
from .models import WordEntryModel
from .processors import create_grammatical_properties
from .schema import get_word_schema
from .migrations import migrate_word
from storage.repository import Repository

class ConlangProcessor(DomainProcessor):
    """Processor for conlang domain."""
    
    def __init__(self):
        """Initialize the processor."""
        self.repository = Repository(
            storage_dir=os.path.join("storage", "conlang"),
            schema=get_word_schema(),
            domain="conlang"
        )
    
    def get_schemas(self) -> List[str]:
        """Get the list of schemas supported by the conlang domain."""
        return ["word_schema", "phrase_schema"]
        
    def get_templates(self) -> List[str]:
        """Get the list of templates supported by the conlang domain."""
        return ["word_generation", "pronunciation", "morphology"]
        
    def get_functions(self) -> Dict[str, Any]:
        """Get domain-specific functions for the function registry"""
        return {
            "create_word": self.create_word,
            "create_grammatical_properties": create_grammatical_properties,
            "apply_phonology_rules": None,  # Placeholder - implement as needed
            "generate_pronunciation": None,  # Placeholder - implement as needed
            # Add CRUD operations from parent class
            "create_entry": self.create_entry,
            "update_entry": self.update_entry,
            "get_entry": self.get_entry,
            "search_words": self.search_words,
            "migrate_schema": self.migrate_schema
        }
    
    def create_entry(self, data: Dict[str, Any], **kwargs) -> str:
        """Create a domain entry from data and return its ID."""
        return self.repository.add_entry(data)
    
    def update_entry(self, id: str, data: Dict[str, Any], **kwargs) -> bool:
        """Update an existing domain entry."""
        result = self.repository.update_entry(id, data)
        return result is not None
    
    def get_entry(self, id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Retrieve a domain entry by ID."""
        return self.repository.get_entry(id)
        
    def create_word(self, recipe_data: Dict) -> str:
        """Create a word model from recipe data and add to repository."""
        word_model = WordEntryModel.from_recipe_output(recipe_data)
        return self.repository.add_entry(word_model.model_dump(by_alias=True))
    
    def search_words(self, criteria: Dict) -> List[Dict]:
        """Search for words matching given criteria."""
        return self.repository.search(criteria)
    
    def migrate_schema(self, target_version: str) -> int:
        """Migrate all words to a new schema version."""
        migrated_count = 0
        for entry in self.repository.get_all_entries():
            current_version = entry.get("metadata", {}).get("schema_version")
            if current_version != target_version:
                migrated = migrate_word(entry, target_version)
                self.repository.update_entry(entry["id"], migrated)
                migrated_count += 1
        return migrated_count

# Register the domain
register_domain("conlang", ConlangProcessor)