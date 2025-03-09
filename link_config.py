"""
Module containing the LinkConfig base class and related functionality.
Separated from chain.py to avoid circular imports.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LinkConfig(BaseModel):
    """Base model for step configuration."""
    name: str
    type: str
    description: Optional[str] = None
    output_format: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
