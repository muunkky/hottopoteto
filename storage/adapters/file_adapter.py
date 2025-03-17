"""File-based storage adapter implementation."""
import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from storage.adapters import StorageAdapter, register_adapter
from storage.utils import ensure_directory

class FileStorageAdapter(StorageAdapter):
    """File-based storage adapter that stores data as JSON files."""
    
    def __init__(self, base_dir: str, id_field: str = "id"):
        """
        Initialize with base directory and ID field.
        
        Args:
            base_dir: Base directory for storing files
            id_field: Field to use as ID (defaults to 'id')
        """
        self.base_dir = base_dir
        self.id_field = id_field
        
        # Create the base directory if it doesn't exist
        ensure_directory(base_dir)
        
        # Create subdirectories for entries and indices
        self.entries_dir = os.path.join(base_dir, "entries")
        self.indices_dir = os.path.join(base_dir, "indices")
        ensure_directory(self.entries_dir)
        ensure_directory(self.indices_dir)
    
    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'FileStorageAdapter':
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Configuration dictionary
        
        Returns:
            Initialized adapter instance
        """
        base_dir = config.get("base_dir", "storage/data")
        id_field = config.get("id_field", "id")
        return cls(base_dir=base_dir, id_field=id_field)
    
    def store(self, data: Dict[str, Any], **options) -> str:
        """
        Store data and return an ID.
        
        Args:
            data: Data to store
            **options: Additional options
        
        Returns:
            ID of the stored data
        """
        # Clone the data to avoid modifying the original
        entry = data.copy()
        
        # Generate an ID if not provided
        if self.id_field not in entry or not entry[self.id_field]:
            entry_id = str(uuid.uuid4())
            entry[self.id_field] = entry_id
        else:
            entry_id = entry[self.id_field]
        
        # Add timestamps if not present
        if "created_at" not in entry:
            entry["created_at"] = datetime.now().isoformat()
        if "updated_at" not in entry:
            entry["updated_at"] = datetime.now().isoformat()
        
        # Write to file
        file_path = os.path.join(self.entries_dir, f"{entry_id}.json")
        with open(file_path, 'w') as f:
            json.dump(entry, f, indent=2)
        
        # Update indices
        self._update_indices(entry)
        
        return entry_id
    
    def retrieve(self, id: str, **options) -> Optional[Dict[str, Any]]:
        """
        Retrieve data by ID.
        
        Args:
            id: ID of the data to retrieve
            **options: Additional options
        
        Returns:
            Retrieved data or None if not found
        """
        file_path = os.path.join(self.entries_dir, f"{id}.json")
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error retrieving {id}: {e}")
            return None
    
    def update(self, id: str, data: Dict[str, Any], **options) -> bool:
        """
        Update existing data.
        
        Args:
            id: ID of the data to update
            data: New data (partial update)
            **options: Additional options
        
        Returns:
            True if update was successful, False otherwise
        """
        # Get existing entry
        existing = self.retrieve(id)
        if not existing:
            return False
            
        # Update with new data
        updated = {**existing, **data}
        
        # Update timestamp
        updated["updated_at"] = datetime.now().isoformat()
        
        # Write back to file
        file_path = os.path.join(self.entries_dir, f"{id}.json")
        with open(file_path, 'w') as f:
            json.dump(updated, f, indent=2)
        
        # Update indices
        self._update_indices(updated)
        
        return True
    
    def delete(self, id: str, **options) -> bool:
        """
        Delete data by ID.
        
        Args:
            id: ID of the data to delete
            **options: Additional options
        
        Returns:
            True if deletion was successful, False otherwise
        """
        file_path = os.path.join(self.entries_dir, f"{id}.json")
        if not os.path.exists(file_path):
            return False
            
        # Load entry before deleting (for removing from indices)
        try:
            with open(file_path, 'r') as f:
                entry = json.load(f)
                
            # Remove from indices
            self._remove_from_indices(entry)
            
            # Delete file
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting {id}: {e}")
            return False
    
    def search(self, query: Dict[str, Any], **options) -> List[Dict[str, Any]]:
        """
        Search for data matching the query.
        
        Args:
            query: Query parameters
            **options: Additional options
        
        Returns:
            List of matching entries
        """
        # If no query, return all entries
        if not query:
            return self._get_all_entries()
            
        # Simple implementation using in-memory filtering
        results = []
        for entry in self._get_all_entries():
            if self._matches_query(entry, query):
                results.append(entry)
                
        return results
    
    def _get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all entries in the repository."""
        entries = []
        for filename in os.listdir(self.entries_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.entries_dir, filename), 'r') as f:
                        entries.append(json.load(f))
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        return entries
    
    def _matches_query(self, entry: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if an entry matches the query."""
        for key, value in query.items():
            # Handle nested paths (e.g., metadata.tags)
            if "." in key:
                parts = key.split(".")
                current = entry
                for part in parts[:-1]:
                    if part not in current:
                        return False
                    current = current[part]
                    
                if parts[-1] not in current or current[parts[-1]] != value:
                    return False
            
            # Handle special contains operator
            elif key.endswith("_contains"):
                field = key[:-9]  # Remove _contains suffix
                if field not in entry or not isinstance(entry[field], str) or value not in entry[field]:
                    return False
                    
            # Direct field match
            elif key not in entry or entry[key] != value:
                return False
                
        return True
    
    def _update_indices(self, entry: Dict[str, Any]) -> None:
        """Update indices with an entry."""
        # Simple implementation
        # In a real implementation, would create proper indices
        # for fast lookups on common fields
        pass
        
    def _remove_from_indices(self, entry: Dict[str, Any]) -> None:
        """Remove an entry from indices."""
        # Simple implementation
        pass

# Register the file storage adapter
register_adapter("file", FileStorageAdapter)
