"""
Model definitions for storage domain
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, ClassVar, Type
from pydantic import BaseModel, Field
from datetime import datetime
from core.models import GenericEntryModel
from .utils import ensure_directory, safe_load_json, safe_save_json  # Import from utils instead of functions

logger = logging.getLogger(__name__)

# Data models
class StorageEntity(GenericEntryModel):
    """Base model for stored entities"""
    collection: str
    data: Dict[str, Any] = Field(default_factory=dict)
    
class StorageQuery(BaseModel):
    """Query parameters for storage operations"""
    collection: str
    filter: Dict[str, Any] = Field(default_factory=dict)
    limit: Optional[int] = None
    skip: Optional[int] = None

# Service models (adapters integrated here)
class StorageAdapter(BaseModel):
    """Base model for storage adapters"""
    name: str
    collection: str
    
    # Use class variable for registry
    _registry: ClassVar[Dict[str, Type['StorageAdapter']]] = {}
    
    def save(self, id: str, data: Dict[str, Any]) -> bool:
        """Save data with the given ID"""
        raise NotImplementedError("Storage adapters must implement save method")
        
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get data with the given ID"""
        raise NotImplementedError("Storage adapters must implement get method")
        
    def delete(self, id: str) -> bool:
        """Delete data with the given ID"""
        raise NotImplementedError("Storage adapters must implement delete method")
        
    def query(self, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query data with filter criteria"""
        raise NotImplementedError("Storage adapters must implement query method")
    
    @classmethod
    def register(cls, adapter_class: Type['StorageAdapter']) -> None:
        """Register an adapter implementation"""
        cls._registry[adapter_class.__fields__["name"].default] = adapter_class
        
    @classmethod
    def get(cls, name: str) -> Optional[Type['StorageAdapter']]:
        """Get an adapter by name"""
        return cls._registry.get(name)
        
    @classmethod
    def list(cls) -> List[str]:
        """List all registered adapters"""
        return list(cls._registry.keys())

class FileAdapter(StorageAdapter):
    """File-based storage adapter"""
    name: str = "file"
    base_dir: str = Field(default="storage/data")
    
    def _get_file_path(self, id: str) -> str:
        """Get the file path for an entity"""
        return os.path.join(self.base_dir, self.collection, f"{id}.json")
    
    def save(self, id: str, data: Dict[str, Any]) -> bool:
        """Save data with the given ID"""
        file_path = self._get_file_path(id)
        return safe_save_json(file_path, data)
    
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get data with the given ID"""
        file_path = self._get_file_path(id)
        return safe_load_json(file_path)
            
    def delete(self, id: str) -> bool:
        """Delete data with the given ID"""
        file_path = self._get_file_path(id)
        if not os.path.exists(file_path):
            return False
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
            
    def query(self, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query data with filter criteria"""
        results = []
        collection_dir = os.path.join(self.base_dir, self.collection)
        
        if not os.path.exists(collection_dir):
            return []
                
        for filename in os.listdir(collection_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(collection_dir, filename)
                    entity = safe_load_json(file_path)
                    
                    # Apply filters
                    if self._matches_criteria(entity, filter_criteria):
                        results.append(entity)
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {e}")
                        
        return results
    
    def _matches_criteria(self, entity: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if an entity matches the filter criteria"""
        if not criteria:
            return True
            
        for key, value in criteria.items():
            if '.' in key:
                # Handle nested fields
                parts = key.split('.')
                current = entity
                for part in parts[:-1]:
                    if part not in current:
                        return False
                    current = current[part]
                if parts[-1] not in current or current[parts[-1]] != value:
                    return False
            elif key not in entity or entity[key] != value:
                return False
                
        return True

# Register adapter implementations
StorageAdapter.register(FileAdapter)

# Register schemas with domain schema registry
from core.registration import register_domain_schema

register_domain_schema("storage", "entity", StorageEntity.schema())
register_domain_schema("storage", "query", StorageQuery.schema())
