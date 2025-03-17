import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from jsonschema import validate, ValidationError
import jsonschema

from storage.utils import repair_entry
from storage.indexing import update_indices, search_by_criteria

# Add a custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class Repository:
    """
    Generic repository for storing and retrieving entries.
    Handles CRUD operations, indexing, and schema validation.
    """
    
    def __init__(self, storage_dir: str, schema=None, domain=None):
        """Initialize the repository with directory configuration"""
        self.storage_dir = storage_dir
        self.domain = domain
        
        # Check if the parent directory is writable
        parent = os.path.dirname(os.path.abspath(storage_dir))
        if not os.access(parent, os.W_OK):
            raise Exception(f"Parent directory {parent} is not writable")
            
        self.schema = schema
        self.entries_dir = os.path.join(storage_dir, "entries")
        self.indices_dir = os.path.join(storage_dir, "indices")
        
        # Create directories if they don't exist
        os.makedirs(self.entries_dir, exist_ok=True)
        os.makedirs(self.indices_dir, exist_ok=True)
    
    def add_entry(self, entry: Dict, validate: bool = True) -> str:
        """
        Add an entry to the repository, performing schema validation.
        Returns the ID of the added entry.
        """
        # Make a copy to avoid modifying the original
        entry_data = entry.copy()
            
        # Convert datetime objects in metadata to strings before validation
        if "metadata" in entry_data:
            for field in ["created_at", "updated_at"]:
                if field in entry_data["metadata"] and isinstance(entry_data["metadata"][field], datetime):
                    entry_data["metadata"][field] = entry_data["metadata"][field].isoformat()

        # Handle any timestamps
        if "created_at" in entry_data and isinstance(entry_data["created_at"], datetime):
            entry_data["created_at"] = entry_data["created_at"].isoformat()
        
        # Always repair the entry first to fix any issues
        if self.schema:
            entry_data = repair_entry(entry_data, self.schema)
        
        # Validate against schema if requested and schema exists
        if validate and self.schema:
            try:
                jsonschema.validate(instance=entry_data, schema=self.schema)
                logging.info(f"Entry validated successfully against schema")
            except jsonschema.exceptions.ValidationError as e:
                logging.error(f"Entry failed schema validation: {e}")
                raise ValueError(f"Schema validation failed: {e}")
        
        # Get the entry ID - assumes entry has an ID field
        if "id" in entry_data:
            entry_id = entry_data["id"]
        else:
            raise ValueError("Entry must have an 'id' field")
        
        # Save the entry file
        entry_file_path = os.path.join(self.entries_dir, f"{entry_id}.json")
        with open(entry_file_path, 'w') as f:
            json.dump(entry_data, f, indent=2, cls=DateTimeEncoder)
            
        # Update indices
        update_indices(entry_data, self.indices_dir)
        
        return entry_id
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """Retrieve an entry by its ID."""
        entry_path = os.path.join(self.entries_dir, f"{entry_id}.json")
            
        if not os.path.exists(entry_path):
            return None
            
        try:
            with open(entry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Error loading entry {entry_id}: {e}")
    
    def update_entry(self, entry_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing entry with new data"""
        current_entry = self.get_entry(entry_id)
        if not current_entry:
            return None
            
        # Apply updates
        for key, value in updates.items():
            if key in current_entry:
                if isinstance(current_entry[key], dict) and isinstance(value, dict):
                    # Deep merge dictionaries
                    current_entry[key] = {**current_entry[key], **value}
                else:
                    current_entry[key] = value
                    
        # Update metadata
        if "metadata" in current_entry:
            current_entry["metadata"]["updated_at"] = datetime.now().isoformat()
        
        # Re-validate if schema exists
        if self.schema:
            try:
                validate(instance=current_entry, schema=self.schema)
            except ValidationError as e:
                raise ValueError(f"Updated entry failed schema validation: {e}")
            
        # Save the updated entry
        entry_path = os.path.join(self.entries_dir, f"{entry_id}.json")
        with open(entry_path, 'w') as f:
            json.dump(current_entry, f, indent=2, cls=DateTimeEncoder)
            
        # Update indices
        update_indices(current_entry, self.indices_dir)
        
        return current_entry
    
    def delete_entry(self, entry_id: str) -> bool:
        """Remove an entry from the repository"""
        entry_path = os.path.join(self.entries_dir, f"{entry_id}.json")
        if not os.path.exists(entry_path):
            return False
            
        # Get the entry data to remove from indices
        try:
            with open(entry_path, 'r') as f:
                entry_data = json.load(f)
                
            # Delete the file
            os.remove(entry_path)
            
            # Remove from indices (would need implementation)
            self._remove_from_indices(entry_data)
            
            return True
        except Exception as e:
            raise IOError(f"Error deleting entry {entry_id}: {e}")
    
    def search(self, criteria: Dict) -> List[Dict]:
        """Search for entries matching the given criteria"""
        return search_by_criteria(criteria, self.storage_dir)
    
    def get_all_entries(self) -> List[Dict]:
        """Get all entries in the repository"""
        results = []
        for filename in os.listdir(self.entries_dir):
            if filename.endswith('.json'):
                entry_path = os.path.join(self.entries_dir, filename)
                try:
                    with open(entry_path, 'r') as f:
                        entry_data = json.load(f)
                        results.append(entry_data)
                except Exception as e:
                    logging.error(f"Error loading entry {filename}: {e}")
        return results
    
    def _get_all_entry_ids(self) -> List[str]:
        """Get all entry IDs in the repository"""
        entry_ids = []
        for filename in os.listdir(self.entries_dir):
            if filename.endswith('.json'):
                entry_id = filename.replace('.json', '')
                entry_ids.append(entry_id)
        return entry_ids
    
    def _remove_from_indices(self, entry_data: Dict) -> None:
        """Remove an entry from all indices"""
        # Implementation depends on how indices are stored
        pass
