"""
Link handlers for recipe execution.
"""
from typing import Dict, Any, Type, Optional, List
import logging
import importlib
import os

logger = logging.getLogger(__name__)

# Dictionary for storing registered link handlers
_link_handlers = {}

class LinkHandler:
    """Base class for all link handlers."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a link with the given configuration and context.
        
        Args:
            link_config: The link configuration
            context: Execution context with previous link outputs
            
        Returns:
            Dictionary with 'raw' and 'data' keys
        """
        raise NotImplementedError("Link handlers must implement execute method")
        
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get the JSON schema for this link type's configuration.
        
        Returns:
            JSON schema dictionary
        """
        raise NotImplementedError("Link handlers must implement get_schema method")

def register_link_type(link_type: str, handler_class: Type[LinkHandler]) -> None:
    """
    Register a link handler for a specific link type.
    
    Args:
        link_type: The link type identifier (e.g., "llm", "storage.save")
        handler_class: The handler class that implements LinkHandler
    """
    _link_handlers[link_type] = handler_class
    logger.info(f"Registered link handler for type: {link_type}")

def get_link_handler(link_type: str) -> Optional[Type[LinkHandler]]:
    """
    Get a handler for a specific link type.
    
    Args:
        link_type: The link type identifier
        
    Returns:
        The handler class or None if not found
    """
    return _link_handlers.get(link_type)

def list_link_types() -> List[str]:
    """
    List all registered link types.
    
    Returns:
        List of link type identifiers
    """
    return list(_link_handlers.keys())

# Modified to discover links in domain packages
def discover_links() -> None:
    """Discover and register links from core domains"""
    # Load core links first
    current_dir = os.path.dirname(__file__)
    for file in os.listdir(current_dir):
        if file.endswith('.py') and file != '__init__.py':
            module_name = file[:-3]  # Remove .py extension
            try:
                importlib.import_module(f"core.links.{module_name}")
                logger.debug(f"Loaded core link handler module: {module_name}")
            except ImportError as e:
                logger.error(f"Error loading core link handler module {module_name}: {e}")
    
    # Then discover domain-specific links
    domains_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "domains")
    if os.path.exists(domains_dir):
        for domain_name in os.listdir(domains_dir):
            domain_path = os.path.join(domains_dir, domain_name)
            if os.path.isdir(domain_path) and not domain_name.startswith("__"):
                links_file = os.path.join(domain_path, "links.py")
                if os.path.exists(links_file):
                    try:
                        # Use a try-except block to continue even if one domain fails
                        module_name = f"core.domains.{domain_name}.links"
                        try:
                            importlib.import_module(module_name)
                            logger.debug(f"Loaded domain link handlers: {domain_name}")
                        except ImportError as e:
                            logger.warning(f"Error loading domain links for {domain_name}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error loading domain links for {domain_name}: {e}")
    
# Automatically discover links when this module is imported
discover_links()
