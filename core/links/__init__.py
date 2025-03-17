"""Link type registry and base classes."""
from typing import Dict, Any, Type, Callable

# Registry of available link types
_link_handlers = {}

class LinkHandler:
    """Base class for link type handlers."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute this link type with the given configuration and context."""
        raise NotImplementedError("Link handlers must implement execute()")
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for this link type's configuration."""
        raise NotImplementedError("Link handlers must implement get_schema()")

def register_link_type(name: str, handler_class: Type[LinkHandler]) -> None:
    """Register a link type handler."""
    _link_handlers[name] = handler_class
    
def get_link_handler(name: str) -> Type[LinkHandler]:
    """Get a link type handler by name."""
    if name not in _link_handlers:
        raise ValueError(f"Unknown link type: {name}")
    return _link_handlers[name]

def get_registered_link_types() -> Dict[str, Type[LinkHandler]]:
    """Get all registered link types."""
    return _link_handlers.copy()
