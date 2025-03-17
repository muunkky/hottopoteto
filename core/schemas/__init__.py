from typing import Dict, Any

_schema_registry = {}

def register_schema(name: str, schema: Dict[str, Any]) -> None:
    """Register a schema with the system."""
    _schema_registry[name] = schema
    
def get_schema(name: str) -> Dict[str, Any]:
    """Get a registered schema by name."""
    if name not in _schema_registry:
        raise ValueError(f"Unknown schema: {name}")
    return _schema_registry[name]

def list_schemas() -> list[str]:
    """List all registered schemas."""
    return list(_schema_registry.keys())
