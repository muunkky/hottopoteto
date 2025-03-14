from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class GenericEntryModel(BaseModel):
    """Base model for all domain entries."""
    id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump()
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenericEntryModel":
        """Create an instance from dictionary data."""
        return cls(**data)