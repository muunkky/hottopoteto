# filepath: c:\Users\Cameron\Projects\langchain\v2\domains\conlang\__init__.py
from ..import DomainProcessor, register_domain
from ...lexicon.models.word import WordEntryModel
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

# Register the domain
register_domain("conlang", ConlangProcessor)