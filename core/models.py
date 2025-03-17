from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class GenericEntryModel(BaseModel):
    """
    Base model for all domain entries.
    This provides common fields that all entries should have regardless of domain.
    """
    id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        data = self.model_dump()
        
        # Convert datetime objects to ISO format strings
        for field in ["created_at", "updated_at"]:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
                
        # Also handle nested metadata dates
        if "metadata" in data:
            for date_field in ["created_at", "updated_at"]:
                if date_field in data["metadata"] and isinstance(data["metadata"][date_field], datetime):
                    data["metadata"][date_field] = data["metadata"][date_field].isoformat()
        
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenericEntryModel":
        """Create an instance from dictionary data."""
        return cls(**data)

class RecipeDefinition(BaseModel):
    """Model representing a recipe definition."""
    name: str
    description: str = ""
    version: str = "1.0"
    domain: str = "generic"
    links: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary."""
        return self.model_dump()