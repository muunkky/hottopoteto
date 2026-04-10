"""
TDD Tests for storage.update link type

Tests the StorageUpdateLink handler which merges new data into existing
documents initialized by storage.init.

Test Categories:
1. Registration - Link type is registered and accessible
2. Document Retrieval - Gets existing document by ID
3. Data Merging - Merges new data into existing document
4. Schema Validation - Validates merged data against schema
5. Nested Merging - Handles nested objects correctly
6. Array Handling - Append vs replace for arrays
7. Persistence - Saves updated document
8. Output Structure - Returns correct output format
9. Error Handling - Handles missing documents, invalid data
10. Link Schema - Provides valid JSON schema
"""
import pytest
from unittest.mock import patch, MagicMock
from core.links import get_link_handler
from core.domains.storage.links import StorageUpdateLink


# ==============================================================================
# Test Category 1: Registration
# ==============================================================================

class TestStorageUpdateLinkRegistration:
    """Tests for storage.update link type registration."""
    
    def test_storage_update_is_registered(self):
        """storage.update should be registered as a link type."""
        handler = get_link_handler("storage.update")
        assert handler is not None
    
    def test_storage_update_returns_correct_handler(self):
        """storage.update should return StorageUpdateLink handler."""
        handler = get_link_handler("storage.update")
        assert handler == StorageUpdateLink
    
    def test_storage_update_has_execute_method(self):
        """StorageUpdateLink should have an execute method."""
        assert hasattr(StorageUpdateLink, "execute")
        assert callable(getattr(StorageUpdateLink, "execute"))


# ==============================================================================
# Test Category 2: Document Retrieval
# ==============================================================================

class TestStorageUpdateDocumentRetrieval:
    """Tests for retrieving existing documents."""
    
    @patch('core.domains.storage.links.Repository')
    def test_retrieves_document_by_id(self, mock_repo_class):
        """Should retrieve existing document by document_id."""
        # Setup mock
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-abc123",
            "data": {"field1": "value1"},
            "metadata": {"schema": {"type": "object", "properties": {"field1": {"type": "string"}}}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-abc123",
            "collection": "test_collection",
            "data": {"field2": "value2"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        mock_repo.get.assert_called_once_with("doc-abc123")
    
    @patch('core.domains.storage.links.Repository')
    def test_renders_document_id_template(self, mock_repo_class):
        """Should render Jinja2 templates in document_id."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-xyz789",
            "data": {"existing": "data"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "{{ Working_Doc.data.id }}",
            "collection": "test_collection",
            "data": {"new": "data"}
        }
        context = {
            "Working_Doc": {"data": {"id": "doc-xyz789"}}
        }
        
        result = StorageUpdateLink.execute(config, context)
        
        mock_repo.get.assert_called_once_with("doc-xyz789")


# ==============================================================================
# Test Category 3: Data Merging (Default Behavior)
# ==============================================================================

class TestStorageUpdateDataMerging:
    """Tests for merging new data into existing documents."""
    
    @patch('core.domains.storage.links.Repository')
    def test_merge_adds_new_fields(self, mock_repo_class):
        """Merging should add new fields without removing existing ones."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field1": "value1"},
            "metadata": {"schema": {"type": "object", "properties": {}}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"field2": "value2"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        # Verify merged data was saved
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["data"]["field1"] == "value1"
        assert saved_entity["data"]["field2"] == "value2"
    
    @patch('core.domains.storage.links.Repository')
    def test_merge_updates_existing_fields(self, mock_repo_class):
        """Merging should update values of existing fields."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field1": "old_value"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"field1": "new_value"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["data"]["field1"] == "new_value"
    
    @patch('core.domains.storage.links.Repository')
    def test_merge_is_default_behavior(self, mock_repo_class):
        """Merge should be the default behavior when merge option not specified."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"existing": "value"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        # No 'merge' option specified
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new": "data"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        # Should have both existing and new data
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["data"]["existing"] == "value"
        assert saved_entity["data"]["new"] == "data"
    
    @patch('core.domains.storage.links.Repository')
    def test_replace_when_merge_false(self, mock_repo_class):
        """When merge=False, should replace entire data."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"existing": "value", "other": "data"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new": "data"},
            "merge": False
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        # Should only have new data
        saved_entity = mock_repo.save.call_args[0][1]
        assert "existing" not in saved_entity["data"]
        assert saved_entity["data"]["new"] == "data"


# ==============================================================================
# Test Category 4: Schema Validation
# ==============================================================================

class TestStorageUpdateSchemaValidation:
    """Tests for validating merged data against schema."""
    
    @patch('core.domains.storage.links.Repository')
    def test_validates_merged_data_against_schema(self, mock_repo_class):
        """Should validate merged data against stored schema."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"name": "Test"},
            "metadata": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "count": {"type": "integer"}
                    }
                }
            }
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"count": 42}  # Valid integer
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert result["data"].get("success", True) is not False
    
    @patch('core.domains.storage.links.Repository')
    def test_returns_error_on_validation_failure(self, mock_repo_class):
        """Should return error when merged data fails schema validation."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"name": "Test"},
            "metadata": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "count": {"type": "integer"}
                    }
                }
            }
        }
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"count": "not_an_integer"}  # Invalid type
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        # Should report validation error
        assert result["data"].get("success") is False or "error" in result["data"]
    
    @patch('core.domains.storage.links.Repository')
    def test_succeeds_with_no_schema(self, mock_repo_class):
        """Should succeed when document has no schema (no validation)."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"anything": "goes"},
            "metadata": {}  # No schema
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new_field": ["any", "type", 123]}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert "error" not in result.get("data", {})


# ==============================================================================
# Test Category 5: Nested Object Merging
# ==============================================================================

class TestStorageUpdateNestedMerging:
    """Tests for merging nested objects."""
    
    @patch('core.domains.storage.links.Repository')
    def test_deep_merge_nested_objects(self, mock_repo_class):
        """Should deep merge nested objects."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {
                "user": {
                    "name": "Alice",
                    "address": {"city": "NYC"}
                }
            },
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {
                "user": {
                    "address": {"country": "USA"}
                }
            }
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        saved_entity = mock_repo.save.call_args[0][1]
        # Original fields preserved
        assert saved_entity["data"]["user"]["name"] == "Alice"
        assert saved_entity["data"]["user"]["address"]["city"] == "NYC"
        # New fields added
        assert saved_entity["data"]["user"]["address"]["country"] == "USA"
    
    @patch('core.domains.storage.links.Repository')
    def test_merge_replaces_null_with_data(self, mock_repo_class):
        """Should replace null values with actual data."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {
                "english_word": "woman",
                "origin_words": None
            },
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {
                "origin_words": [
                    {"word": "fael", "meaning": "grace"}
                ]
            }
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["data"]["origin_words"] == [{"word": "fael", "meaning": "grace"}]


# ==============================================================================
# Test Category 6: Array Handling
# ==============================================================================

class TestStorageUpdateArrayHandling:
    """Tests for array merge/replace behavior."""
    
    @patch('core.domains.storage.links.Repository')
    def test_arrays_replace_by_default(self, mock_repo_class):
        """Arrays should be replaced by default (not appended)."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"tags": ["old", "tags"]},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"tags": ["new", "tags"]}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["data"]["tags"] == ["new", "tags"]
    
    @patch('core.domains.storage.links.Repository')
    def test_arrays_append_when_specified(self, mock_repo_class):
        """Arrays should append when array_merge='append' is set."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"items": ["existing"]},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"items": ["new_item"]},
            "array_merge": "append"
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["data"]["items"] == ["existing", "new_item"]


# ==============================================================================
# Test Category 7: Persistence
# ==============================================================================

class TestStorageUpdatePersistence:
    """Tests for persisting updated documents."""
    
    @patch('core.domains.storage.links.Repository')
    def test_saves_updated_document(self, mock_repo_class):
        """Should save the updated document to storage."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field": "value"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new_field": "new_value"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        mock_repo.save.assert_called_once()
    
    @patch('core.domains.storage.links.Repository')
    def test_preserves_metadata_on_update(self, mock_repo_class):
        """Should preserve original metadata when updating."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field": "value"},
            "metadata": {
                "schema": {"type": "object"},
                "collection": "test_collection",
                "initialized_at": "2025-01-01T00:00:00"
            }
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new": "data"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        saved_entity = mock_repo.save.call_args[0][1]
        assert saved_entity["metadata"]["initialized_at"] == "2025-01-01T00:00:00"
        assert "updated_at" in saved_entity["metadata"]


# ==============================================================================
# Test Category 8: Output Structure
# ==============================================================================

class TestStorageUpdateOutputStructure:
    """Tests for output format."""
    
    @patch('core.domains.storage.links.Repository')
    def test_returns_raw_and_data(self, mock_repo_class):
        """Should return both raw message and structured data."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field": "value"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new": "data"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert "raw" in result
        assert "data" in result
    
    @patch('core.domains.storage.links.Repository')
    def test_data_contains_expected_fields(self, mock_repo_class):
        """Data should contain id, collection, schema, and updated data."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"existing": "value"},
            "metadata": {"schema": {"type": "object"}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new": "data"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert result["data"]["id"] == "doc-123"
        assert result["data"]["collection"] == "test_collection"
        assert result["data"]["schema"] == {"type": "object"}
        assert result["data"]["data"]["existing"] == "value"
        assert result["data"]["data"]["new"] == "data"


# ==============================================================================
# Test Category 9: Error Handling
# ==============================================================================

class TestStorageUpdateErrorHandling:
    """Tests for error handling."""
    
    @patch('core.domains.storage.links.Repository')
    def test_handles_document_not_found(self, mock_repo_class):
        """Should return error when document not found."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = None  # Document not found
        
        config = {
            "type": "storage.update",
            "document_id": "nonexistent-doc",
            "collection": "test_collection",
            "data": {"field": "value"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert result["data"].get("success") is False
        assert "error" in result["data"]
        assert "not found" in result["data"]["error"].lower()
    
    def test_handles_missing_document_id(self):
        """Should return error when document_id not provided."""
        config = {
            "type": "storage.update",
            "collection": "test_collection",
            "data": {"field": "value"}
            # Missing document_id
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert result["data"].get("success") is False
        assert "error" in result["data"]
    
    def test_handles_missing_collection(self):
        """Should return error when collection not provided."""
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            # Missing collection
            "data": {"field": "value"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert result["data"].get("success") is False
        assert "error" in result["data"]
    
    @patch('core.domains.storage.links.Repository')
    def test_handles_save_failure(self, mock_repo_class):
        """Should return error when save fails."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field": "value"},
            "metadata": {}
        }
        mock_repo.save.return_value = False  # Save fails
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {"new": "data"}
        }
        
        result = StorageUpdateLink.execute(config, {})
        
        assert result["data"].get("success") is False


# ==============================================================================
# Test Category 10: Link Schema
# ==============================================================================

class TestStorageUpdateLinkSchema:
    """Tests for link type JSON schema."""
    
    def test_has_get_schema_method(self):
        """Should have get_schema class method."""
        assert hasattr(StorageUpdateLink, "get_schema")
        assert callable(getattr(StorageUpdateLink, "get_schema"))
    
    def test_schema_includes_required_fields(self):
        """Schema should define type, document_id, collection as required."""
        schema = StorageUpdateLink.get_schema()
        
        assert "required" in schema
        assert "type" in schema["required"]
        assert "document_id" in schema["required"]
        assert "collection" in schema["required"]
    
    def test_schema_includes_properties(self):
        """Schema should define all link properties."""
        schema = StorageUpdateLink.get_schema()
        
        props = schema.get("properties", {})
        assert "type" in props
        assert "document_id" in props
        assert "collection" in props
        assert "data" in props
        assert "merge" in props


# ==============================================================================
# Test Category 11: Template Rendering in Data
# ==============================================================================

class TestStorageUpdateTemplateRendering:
    """Tests for Jinja2 template rendering in data."""
    
    @patch('core.domains.storage.links.Repository')
    def test_renders_templates_in_data_values(self, mock_repo_class):
        """Should render Jinja2 templates in data values."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get.return_value = {
            "id": "doc-123",
            "data": {"field": "value"},
            "metadata": {"schema": {}}
        }
        mock_repo.save.return_value = True
        
        config = {
            "type": "storage.update",
            "document_id": "doc-123",
            "collection": "test_collection",
            "data": {
                "extracted_data": "{{ Extract_Origins.data }}"
            }
        }
        context = {
            "Extract_Origins": {
                "data": [{"word": "fael", "meaning": "grace"}]
            }
        }
        
        result = StorageUpdateLink.execute(config, context)
        
        saved_entity = mock_repo.save.call_args[0][1]
        # The template should be rendered with the context value
        assert "extracted_data" in saved_entity["data"]
