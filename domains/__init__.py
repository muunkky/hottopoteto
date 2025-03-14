# filepath: c:\Users\Cameron\Projects\langchain\v2\lexicon\domains\__init__.py
from typing import Dict, Any, List, Type
from abc import ABC, abstractmethod

class DomainProcessor(ABC):
    """Base class for domain-specific processing."""
    
    @abstractmethod
    def process_recipe_output(self, recipe_output: Dict) -> Any:
        """Process recipe output into domain-specific model."""
        pass
        
    @abstractmethod
    def get_schemas(self) -> List[str]:
        """Get the list of schemas supported by this domain."""
        pass
        
    @abstractmethod
    def get_templates(self) -> List[str]:
        """Get the list of templates supported by this domain."""
        pass

# Domain registry
_domain_processors = {}

def register_domain(name: str, processor: Type[DomainProcessor]):
    """Register a domain processor."""
    _domain_processors[name] = processor()
    
def get_domain_processor(name: str) -> DomainProcessor:
    """Get a domain processor by name."""
    if name not in _domain_processors:
        raise ValueError(f"Domain {name} not registered")
    return _domain_processors[name]