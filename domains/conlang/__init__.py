"""
Conlang domain module for processing constructed language data.
"""

from ..import DomainProcessor, register_domain
from ...lexicon.models.word import WordEntryModel
from .processors import create_grammatical_properties
from domains.conlang.processors import create_grammatical_properties
from typing import Dict, Any, List

class ConlangProcessor(DomainProcessor):
    """Processor for conlang domain."""
    
    def process_recipe_output(self, recipe_output: Dict) -> WordEntryModel:
        """Process recipe output into a word entry."""
        return WordEntryModel.from_recipe_output(recipe_output)
        
    def get_schemas(self) -> List[str]:
        """Get the list of schemas supported by the conlang domain."""
        return ["word_schema", "phrase_schema"]
        
    def get_templates(self) -> List[str]:
        """Get the list of templates supported by the conlang domain."""
        return ["word_generation", "pronunciation", "morphology"]
        
    def get_functions(self):
        """Get domain-specific functions for the function registry"""
        return {
            "create_grammatical_properties": create_grammatical_properties
        }

# Register the domain
register_domain("conlang", ConlangProcessor)