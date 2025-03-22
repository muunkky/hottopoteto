"""
Template registry and utilities.
"""
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Registry of template directories from plugins
_template_directories = {
    "text": ["templates/text"],     # Default directory first
    "recipes": ["templates/recipes"]  # Default directory first
}

def register_template_directory(template_type: str, directory: str) -> None:
    """
    Register a directory containing templates.
    
    Args:
        template_type: Type of templates ('text' or 'recipes')
        directory: Path to the directory
    """
    if template_type not in _template_directories:
        _template_directories[template_type] = ["templates/" + template_type]
        
    if directory not in _template_directories[template_type]:
        _template_directories[template_type].append(directory)
        logger.info(f"Registered {template_type} template directory: {directory}")

def get_template_directories(template_type: str) -> List[str]:
    """
    Get all registered directories for a template type.
    
    Args:
        template_type: Type of templates ('text' or 'recipes')
        
    Returns:
        List of directory paths
    """
    return _template_directories.get(template_type, [])

def resolve_template_path(template_ref: str) -> Optional[str]:
    """
    Resolve a template reference to an actual file path.
    Searches in all registered template directories.
    
    Args:
        template_ref: Either a path or a dotted reference
            
    Returns:
        Actual file path to the template or None if not found
    """
    # Handle direct file paths
    if os.path.exists(template_ref):
        return template_ref
        
    # Handle dotted notation (domain.template_name)
    if "." in template_ref and not template_ref.endswith((".txt", ".md", ".j2", ".yaml", ".yml", ".json")):
        parts = template_ref.split(".")
        if len(parts) == 2:
            domain, name = parts
            
            # Try text templates
            for directory in get_template_directories("text"):
                for ext in [".txt", ".md", ".j2"]:
                    path = os.path.join(directory, domain, f"{name}{ext}")
                    if os.path.exists(path):
                        return path
                        
            # Try recipe templates
            for directory in get_template_directories("recipes"):
                for ext in [".yaml", ".yml", ".json"]:
                    path = os.path.join(directory, domain, f"{name}{ext}")
                    if os.path.exists(path):
                        return path
    
    # Try with standard template prefixes
    for template_type, directories in _template_directories.items():
        for directory in directories:
            path = os.path.join(directory, template_ref)
            if os.path.exists(path):
                return path
                
            # Try without templates/ prefix if it was included
            if template_ref.startswith(f"templates/{template_type}/"):
                rel_path = template_ref[len(f"templates/{template_type}/"):]
                for directory in directories:
                    if directory != f"templates/{template_type}":  # Skip the default directory
                        path = os.path.join(directory, rel_path)
                        if os.path.exists(path):
                            return path
    
    return None

def list_templates(template_type: str = None) -> Dict[str, List[str]]:
    """
    List all available templates.
    
    Args:
        template_type: Optional filter by template type
        
    Returns:
        Dictionary of template type to list of template paths
    """
    result = {}
    
    template_types = [template_type] if template_type else _template_directories.keys()
    
    for t_type in template_types:
        result[t_type] = []
        for directory in get_template_directories(t_type):
            if os.path.exists(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        if t_type == "text" and file.endswith((".txt", ".md", ".j2")):
                            result[t_type].append(os.path.join(root, file))
                        elif t_type == "recipes" and file.endswith((".yaml", ".yml", ".json")):
                            result[t_type].append(os.path.join(root, file))
    
    return result
