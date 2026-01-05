"""
TDD Tests for StorageInitLink (storage.init link type)

Step 3 of DOCENRICH Sprint - Schema-Driven Document Enrichment

Tests follow TDD pattern:
1. Write failing tests first (RED)
2. Implement minimum code to pass (GREEN)
3. Refactor for clarity (REFACTOR)

Per ADR-0006, storage.init creates a "working document" that:
- Has a unique ID for tracking
- Includes the schema for downstream LLM links to reference
- Persists data to storage for future updates
- Supports initial_data for pre-populating known fields
"""
import pytest
import os
import yaml
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


# =============================================================================
# Test Setup Fixtures
# =============================================================================

@pytest.fixture
def sample_schema():
    """Minimal JSON Schema for testing."""
    return {
        "type": "object",
        "properties": {
            "english_word": {"type": "string"},
            "eldorian_word": {"type": "string"},
            "origin_words": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["english_word"]
    }


@pytest.fixture
def sample_context():
    """Sample execution context with memory."""
    return {
        "user_input": {
            "data": {
                "word": "woman",
                "connotation": "of marriageable age"
            }
        }
    }


@pytest.fixture
def temp_schema_file(tmp_path, sample_schema):
    """Create a temporary schema file."""
    schema_dir = tmp_path / "templates" / "schemas"
    schema_dir.mkdir(parents=True)
    schema_file = schema_dir / "test_schema.yaml"
    schema_file.write_text(yaml.dump(sample_schema))
    return schema_file


# =============================================================================
# Test: StorageInitLink Class Exists and Is Registered
# =============================================================================

class TestStorageInitLinkRegistration:
    """Test that storage.init link type is properly registered."""
    
    def test_storage_init_link_class_exists(self):
        """Storage init link class should exist."""
        from core.domains.storage.links import StorageInitLink
        assert StorageInitLink is not None
    
    def test_storage_init_is_registered_link_type(self):
        """storage.init should be a registered link type."""
        from core.links import get_link_handler
        link_cls = get_link_handler("storage.init")
        assert link_cls is not None
    
    def test_storage_init_has_execute_method(self):
        """StorageInitLink should have execute class method."""
        from core.domains.storage.links import StorageInitLink
        assert hasattr(StorageInitLink, 'execute')
        assert callable(getattr(StorageInitLink, 'execute'))


# =============================================================================
# Test: Document Creation and ID Generation
# =============================================================================

class TestStorageInitDocumentCreation:
    """Test document creation behavior."""
    
    def test_execute_creates_document_with_unique_id(self):
        """Execute should create document with unique ID."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"type": "object", "properties": {}}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        assert "data" in result
        assert "id" in result["data"]
        assert result["data"]["id"] is not None
        assert len(result["data"]["id"]) > 0
    
    def test_execute_returns_collection_name(self):
        """Execute should return the collection name in output."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "my_collection",
            "schema": {"type": "object", "properties": {}}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        assert result["data"]["collection"] == "my_collection"
    
    def test_execute_generates_unique_ids(self):
        """Multiple executions should generate unique IDs."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"type": "object", "properties": {}}
        }
        
        ids = []
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            for _ in range(5):
                result = StorageInitLink.execute(link_config, {})
                ids.append(result["data"]["id"])
        
        # All IDs should be unique
        assert len(ids) == len(set(ids)), "IDs should be unique"


# =============================================================================
# Test: Schema Resolution
# =============================================================================

class TestStorageInitSchemaResolution:
    """Test schema loading and resolution."""
    
    def test_execute_with_inline_schema(self):
        """Execute should work with inline schema."""
        from core.domains.storage.links import StorageInitLink
        
        inline_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": inline_schema
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        assert result["data"]["schema"] == inline_schema
    
    def test_execute_with_file_schema_reference(self, tmp_path, sample_schema):
        """Execute should resolve file schema references."""
        from core.domains.storage.links import StorageInitLink
        
        # Create schema file
        schema_dir = tmp_path / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "test.yaml"
        schema_file.write_text(yaml.dump(sample_schema))
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"file": str(schema_file)}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        assert result["data"]["schema"] == sample_schema
    
    def test_execute_returns_schema_for_downstream_links(self):
        """Schema should be included in output for LLM links to reference."""
        from core.domains.storage.links import StorageInitLink
        
        schema = {
            "type": "object",
            "properties": {
                "english_word": {"type": "string", "description": "The English word"},
                "translation": {"type": "string", "description": "The translated word"}
            }
        }
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": schema
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        # Schema should be in output so downstream links can access:
        # {{ Test_Doc.data.schema.properties.english_word.description }}
        assert "schema" in result["data"]
        assert result["data"]["schema"]["properties"]["english_word"]["description"] == "The English word"


# =============================================================================
# Test: Initial Data Population
# =============================================================================

class TestStorageInitInitialData:
    """Test initial data pre-population."""
    
    def test_execute_with_initial_data(self):
        """Execute should pre-populate fields from initial_data."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
            "initial_data": {"name": "test_value"}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        assert result["data"]["data"]["name"] == "test_value"
    
    def test_execute_renders_templates_in_initial_data(self, sample_context):
        """Initial data should support template rendering."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"type": "object", "properties": {"word": {"type": "string"}}},
            "initial_data": {"word": "{{ user_input.data.word }}"}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, sample_context)
        
        assert result["data"]["data"]["word"] == "woman"
    
    def test_execute_initializes_missing_schema_properties_as_null(self):
        """Properties not in initial_data should be null per schema."""
        from core.domains.storage.links import StorageInitLink
        
        schema = {
            "type": "object",
            "properties": {
                "provided": {"type": "string"},
                "missing": {"type": "string"},
                "nested": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "number"}
                    }
                }
            }
        }
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": schema,
            "initial_data": {"provided": "has_value"}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        data = result["data"]["data"]
        assert data["provided"] == "has_value"
        assert data["missing"] is None
        assert data["nested"] is None
    
    def test_execute_without_initial_data(self):
        """Execute should work without initial_data (all nulls)."""
        from core.domains.storage.links import StorageInitLink
        
        schema = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "number"}
            }
        }
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": schema
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        data = result["data"]["data"]
        assert data["field1"] is None
        assert data["field2"] is None


# =============================================================================
# Test: Storage Persistence
# =============================================================================

class TestStorageInitPersistence:
    """Test that documents are persisted to storage."""
    
    def test_execute_saves_to_repository(self):
        """Execute should save document to repository."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "my_collection",
            "schema": {"type": "object", "properties": {}}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_instance = Mock()
            mock_instance.save.return_value = True
            mock_repo.return_value = mock_instance
            
            result = StorageInitLink.execute(link_config, {})
        
        # Repository should be created for the collection
        mock_repo.assert_called_with("my_collection")
        
        # Save should be called with ID and entity
        mock_instance.save.assert_called_once()
        save_args = mock_instance.save.call_args
        assert save_args is not None
    
    def test_execute_stores_schema_in_metadata(self):
        """Schema should be stored in document metadata."""
        from core.domains.storage.links import StorageInitLink
        
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": schema
        }
        
        saved_entity = None
        
        def capture_save(doc_id, entity):
            nonlocal saved_entity
            saved_entity = entity
            return True
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_instance = Mock()
            mock_instance.save.side_effect = capture_save
            mock_repo.return_value = mock_instance
            
            StorageInitLink.execute(link_config, {})
        
        # Check metadata contains schema
        assert saved_entity is not None
        assert "metadata" in saved_entity
        assert saved_entity["metadata"]["schema"] == schema


# =============================================================================
# Test: Output Structure
# =============================================================================

class TestStorageInitOutputStructure:
    """Test the output structure matches specification."""
    
    def test_output_has_required_fields(self):
        """Output should have raw and data fields."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"type": "object", "properties": {}}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        assert "raw" in result
        assert "data" in result
    
    def test_output_data_structure(self):
        """Output data should have id, collection, schema, data."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "my_collection",
            "schema": {"type": "object", "properties": {"x": {"type": "string"}}}
        }
        
        with patch('core.domains.storage.links.Repository') as mock_repo:
            mock_repo.return_value.save.return_value = True
            
            result = StorageInitLink.execute(link_config, {})
        
        data = result["data"]
        assert "id" in data
        assert "collection" in data
        assert "schema" in data
        assert "data" in data
        
        assert data["collection"] == "my_collection"
        assert isinstance(data["schema"], dict)
        assert isinstance(data["data"], dict)


# =============================================================================
# Test: Error Handling
# =============================================================================

class TestStorageInitErrorHandling:
    """Test error handling scenarios."""
    
    def test_execute_without_collection_returns_error(self):
        """Execute without collection should return error."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "schema": {"type": "object"}
        }
        
        result = StorageInitLink.execute(link_config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]
    
    def test_execute_with_invalid_schema_file_returns_error(self):
        """Execute with non-existent schema file should handle gracefully."""
        from core.domains.storage.links import StorageInitLink
        
        link_config = {
            "name": "Test_Doc",
            "type": "storage.init",
            "collection": "test_collection",
            "schema": {"file": "nonexistent/schema.yaml"}
        }
        
        result = StorageInitLink.execute(link_config, {})
        
        # Should handle error gracefully
        assert "error" in result["data"] or result["data"].get("success") is False


# =============================================================================
# Test: Schema for Link Type
# =============================================================================

class TestStorageInitLinkSchema:
    """Test the link type schema definition."""
    
    def test_has_get_schema_method(self):
        """StorageInitLink should have get_schema method."""
        from core.domains.storage.links import StorageInitLink
        assert hasattr(StorageInitLink, 'get_schema')
    
    def test_schema_defines_required_properties(self):
        """Link schema should define collection as required."""
        from core.domains.storage.links import StorageInitLink
        
        schema = StorageInitLink.get_schema()
        
        assert "collection" in schema.get("required", [])
