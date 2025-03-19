"""
Template utilities for resolving template references
"""
import os
from typing import Optional
from core.templates import resolve_template_path as registry_resolve_template_path

def resolve_template_path(template_ref: str) -> Optional[str]:
    """
    Resolve a template reference to an actual file path.
    
    Args:
        template_ref: Either a path or a dotted reference
            
    Returns:
        Actual file path to the template
    
    Examples:
        "conlang.word_generation" -> "templates/text/conlang/word_generation.txt"
        "templates/text/system/error.txt" -> "templates/text/system/error.txt"
    """
    # Use the central registry resolver
    return registry_resolve_template_path(template_ref)
