"""
Functions for storage domain
"""
import logging
import uuid
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.registration import register_domain_function
from .models import StorageAdapter
from .utils import ensure_directory, safe_load_json, safe_save_json  # Import from utils

logger = logging.getLogger(__name__)

# Utility functions (moved from utils.py)
def ensure_directory(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False
        
def safe_load_json(file_path: str, default: Any = None) -> Any:
    """
    Safely load a JSON file, returning a default value if loading fails.
    """
    if not os.path.exists(file_path):
        return default if default is not None else {}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return default if default is not None else {}
        
def safe_save_json(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Safely save data to a JSON file.
    """
    try:
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory(directory)
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False

class Repository:
    """Repository for managing entities in a collection."""
    
    def __init__(self, collection_name: str, adapter_name: str = "file"):
        """
        Initialize a repository.
        
        Args:
            collection_name: Name of the collection
            adapter_name: Name of the storage adapter to use
        """
        self.collection_name = collection_name
        
        # Get adapter
        adapter_cls = StorageAdapter.get(adapter_name)
        if not adapter_cls:
            raise ValueError(f"Storage adapter '{adapter_name}' not found")
            
        # Initialize adapter
        self.adapter = adapter_cls(collection=collection_name)
        
    def save(self, id: str, data: Dict[str, Any]) -> bool:
        """Save an entity with the given ID."""
        return self.adapter.save(id, data)
        
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get an entity by ID."""
        return self.adapter.get(id)
        
    def delete(self, id: str) -> bool:
        """Delete an entity by ID."""
        return self.adapter.delete(id)
        
    def query(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query entities with filter criteria."""
        filter_criteria = filter_criteria or {}
        return self.adapter.query(filter_criteria)

# Domain functions that leverage repository pattern
def save_entity(collection: str, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Save an entity to storage
    
    Args:
        collection: Collection name
        data: Entity data
        metadata: Optional metadata
        
    Returns:
        Saved entity with ID
    """
    repository = Repository(collection)
    entity_id = f"{collection.lower()}-{str(uuid.uuid4())[:8]}"
    
    entity = {
        "id": entity_id,
        "data": data,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    
    success = repository.save(entity_id, entity)
    
    if success:
        return {
            "success": True,
            "message": "Entity saved successfully",
            "data": entity
        }
    else:
        return {
            "success": False,
            "error": "Failed to save entity"
        }

def get_entity(collection: str, entity_id: str) -> Dict[str, Any]:
    """Get an entity from storage"""
    repository = Repository(collection)
    entity = repository.get(entity_id)
    
    if entity:
        return {
            "success": True,
            "data": entity
        }
    else:
        return {
            "success": False,
            "error": "Entity not found"
        }

def query_entities(collection: str, filter_criteria: Dict[str, Any] = None, 
                  limit: Optional[int] = None, skip: Optional[int] = None) -> Dict[str, Any]:
    """Query entities from storage"""
    repository = Repository(collection)
    results = repository.query(filter_criteria or {})
    
    # Apply skip and limit if provided
    if skip:
        results = results[skip:]
    if limit:
        results = results[:limit]
        
    return {
        "success": True,
        "results": results,
        "count": len(results)
    }

def delete_entity(collection: str, entity_id: str) -> Dict[str, Any]:
    """Delete an entity from storage"""
    repository = Repository(collection)
    success = repository.delete(entity_id)
    
    if success:
        return {
            "success": True,
            "message": "Entity deleted"
        }
    else:
        return {
            "success": False,
            "error": "Failed to delete entity"
        }

# Register domain functions
register_domain_function("storage", "save_entity", save_entity)
register_domain_function("storage", "get_entity", get_entity)
register_domain_function("storage", "query_entities", query_entities)
register_domain_function("storage", "delete_entity", delete_entity)
