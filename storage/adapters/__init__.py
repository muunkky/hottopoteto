"""Storage adapter registry and base interface."""
from typing import Dict, List, Any, Type, Optional

# Registry of available storage adapters
_storage_adapters = {}

class StorageAdapter:
    """Base interface for storage adapters."""
    
    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'StorageAdapter':
        """Initialize the adapter with configuration."""
        raise NotImplementedError("Storage adapters must implement initialize()")
    
    def store(self, data: Dict[str, Any], **options) -> str:
        """Store data and return an ID."""
        raise NotImplementedError("Storage adapters must implement store()")
        
    def retrieve(self, id: str, **options) -> Optional[Dict[str, Any]]:
        """Retrieve data by ID."""
        raise NotImplementedError("Storage adapters must implement retrieve()")
        
    def update(self, id: str, data: Dict[str, Any], **options) -> bool:
        """Update existing data."""
        raise NotImplementedError("Storage adapters must implement update()")
        
    def delete(self, id: str, **options) -> bool:
        """Delete data by ID."""
        raise NotImplementedError("Storage adapters must implement delete()")
        
    def search(self, query: Dict[str, Any], **options) -> List[Dict[str, Any]]:
        """Search for data matching the query."""
        raise NotImplementedError("Storage adapters must implement search()")

def register_adapter(name: str, adapter_class: Type[StorageAdapter]) -> None:
    """Register a storage adapter."""
    _storage_adapters[name] = adapter_class
    
def get_adapter(name: str) -> Type[StorageAdapter]:
    """Get a storage adapter by name."""
    if name not in _storage_adapters:
        raise ValueError(f"Unknown storage adapter: {name}")
    return _storage_adapters[name]
