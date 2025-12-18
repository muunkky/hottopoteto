"""Tests for core.schemas module."""
import pytest
from core.schemas import register_schema, get_schema, list_schemas, _schemas


class TestSchemaRegistry:
    """Tests for schema registration and retrieval."""
    
    def setup_method(self):
        """Clear schema registry before each test."""
        _schemas.clear()
    
    def test_register_schema_stores_schema(self):
        """Test that register_schema() stores schema in registry."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        register_schema("test.person", schema)
        
        assert "test.person" in _schemas
        assert _schemas["test.person"] == schema
    
    def test_register_multiple_schemas(self):
        """Test registering multiple schemas with different names."""
        schema1 = {"type": "string"}
        schema2 = {"type": "number"}
        schema3 = {"type": "array"}
        
        register_schema("domain1.type1", schema1)
        register_schema("domain1.type2", schema2)
        register_schema("domain2.type1", schema3)
        
        assert len(_schemas) == 3
        assert _schemas["domain1.type1"] == schema1
        assert _schemas["domain1.type2"] == schema2
        assert _schemas["domain2.type1"] == schema3
    
    def test_register_schema_overwrites_existing(self):
        """Test that re-registering a schema name overwrites the old one."""
        old_schema = {"type": "string"}
        new_schema = {"type": "number"}
        
        register_schema("test.overwrite", old_schema)
        assert _schemas["test.overwrite"] == old_schema
        
        register_schema("test.overwrite", new_schema)
        assert _schemas["test.overwrite"] == new_schema
    
    def test_get_schema_returns_registered_schema(self):
        """Test that get_schema() retrieves a registered schema."""
        schema = {"type": "boolean", "description": "Test schema"}
        register_schema("test.bool", schema)
        
        result = get_schema("test.bool")
        
        assert result == schema
        assert result is schema  # Same object reference
    
    def test_get_schema_returns_none_for_unregistered(self):
        """Test that get_schema() returns None for non-existent schema."""
        result = get_schema("nonexistent.schema")
        
        assert result is None
    
    def test_get_schema_with_empty_registry(self):
        """Test get_schema() when no schemas are registered."""
        assert len(_schemas) == 0
        result = get_schema("any.schema")
        assert result is None
    
    def test_list_schemas_returns_all_registered(self):
        """Test that list_schemas() returns all registered schemas."""
        schema1 = {"type": "string"}
        schema2 = {"type": "number"}
        
        register_schema("test.schema1", schema1)
        register_schema("test.schema2", schema2)
        
        all_schemas = list_schemas()
        
        assert len(all_schemas) == 2
        assert all_schemas["test.schema1"] == schema1
        assert all_schemas["test.schema2"] == schema2
    
    def test_list_schemas_returns_empty_dict_when_none_registered(self):
        """Test that list_schemas() returns empty dict when registry is empty."""
        all_schemas = list_schemas()
        
        assert isinstance(all_schemas, dict)
        assert len(all_schemas) == 0
    
    def test_list_schemas_returns_copy_not_reference(self):
        """Test that list_schemas() returns the actual registry dict."""
        schema = {"type": "string"}
        register_schema("test.ref", schema)
        
        result = list_schemas()
        
        # This actually returns a reference to _schemas, not a copy
        assert result is _schemas
    
    def test_schema_with_complex_structure(self):
        """Test registering and retrieving complex nested schema."""
        complex_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "values": {
                            "type": "array",
                            "items": {"type": "number"}
                        },
                        "metadata": {
                            "type": "object",
                            "additionalProperties": True
                        }
                    },
                    "required": ["values"]
                }
            },
            "required": ["id", "data"]
        }
        
        register_schema("complex.nested", complex_schema)
        result = get_schema("complex.nested")
        
        assert result == complex_schema
        assert result["properties"]["data"]["properties"]["values"]["items"]["type"] == "number"
    
    def test_schema_name_formats(self):
        """Test that various schema name formats are supported."""
        register_schema("simple", {"type": "string"})
        register_schema("domain.entity", {"type": "number"})
        register_schema("domain.subdomain.entity", {"type": "boolean"})
        register_schema("domain-with-dashes.entity_underscores", {"type": "array"})
        
        assert get_schema("simple") is not None
        assert get_schema("domain.entity") is not None
        assert get_schema("domain.subdomain.entity") is not None
        assert get_schema("domain-with-dashes.entity_underscores") is not None
