"""
Domain registry and base classes for domain-specific processors.
"""
from typing import Dict, Any, List, Optional, Callable, Type

# Registry of domain processors
_domain_processors = {}

class DomainProcessor:
    """Base class for domain-specific processors."""
    
    def get_functions(self) -> Dict[str, Callable]:
        """
        Get domain-specific functions for the function registry.
        Recipes can call these functions directly during execution.
        """
        return {
            # Example of including CRUD operations 
            "create_entry": self.create_entry,
            "update_entry": self.update_entry,
            "get_entry": self.get_entry,
        }
    
    # New default implementations of common operations
    def create_entry(self, data: Dict[str, Any], **kwargs) -> str:
        """Create a domain entry from data and return its ID."""
        raise NotImplementedError("Domains should implement create_entry")
    
    def update_entry(self, id: str, data: Dict[str, Any], **kwargs) -> bool:
        """Update an existing domain entry."""  
        raise NotImplementedError("Domains should implement update_entry")
    
    def get_entry(self, id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Retrieve a domain entry by ID."""
        raise NotImplementedError("Domains should implement get_entry")
    
    def get_schemas(self) -> List[str]:
        """
        Get the list of schemas supported by this domain.
        
        Returns:
            List of schema names
        """
        return []
    
    def get_templates(self) -> List[str]:
        """
        Get the list of templates supported by this domain.
        
        Returns:
            List of template names
        """
        return []

def register_domain(domain_name: str, processor_class: Type[DomainProcessor]) -> None:
    """
    Register a domain processor.
    
    Args:
        domain_name: The name of the domain
        processor_class: The domain processor class
    """
    _domain_processors[domain_name] = processor_class()

def get_domain_processor(domain_name: str) -> Optional[DomainProcessor]:
    """
    Get a domain processor by name.
    
    Args:
        domain_name: The name of the domain
        
    Returns:
        The domain processor, or None if not found
        
    Raises:
        ValueError: If the domain is not registered
    """
    if domain_name not in _domain_processors:
        raise ValueError(f"Domain '{domain_name}' is not registered")
    return _domain_processors[domain_name]

def get_registered_domains() -> List[str]:
    """
    Get the list of registered domains.
    
    Returns:
        List of domain names
    """
    return list(_domain_processors.keys())

# Import all domain modules to register them
def _import_domains():
    """Import all domain modules to register them."""
    import importlib
    import pkgutil
    import os
    
    # Get the path to the domains directory
    domain_path = os.path.dirname(os.path.abspath(__file__))
    
    # Import each domain module
    for finder, name, ispkg in pkgutil.iter_modules([domain_path]):
        if ispkg:  # Only import packages (directories)
            try:
                importlib.import_module(f".{name}", __package__)
            except ImportError as e:
                print(f"Error importing domain '{name}': {e}")

# Import all domains when this module is loaded
_import_domains()