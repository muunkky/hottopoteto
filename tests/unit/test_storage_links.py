"""
Unit tests for storage domain link handlers

Tests cover:
- Template rendering in storage.save links
- Nested dictionary template rendering
- Edge cases (malformed templates, undefined variables)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.domains.storage.links import StorageSaveLink


class TestStorageSaveLink:
    """Test suite for StorageSaveLink handler"""
    
    def test_storage_save_renders_simple_template_strings(self):
        """Test that simple template strings in dict values are rendered"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "simple_field": "{{ TestLink.data.value }}",
                "literal_field": "no template here"
            },
            "metadata": {
                "source": "test"
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "value": "rendered_value"
                },
                "raw": "raw content"
            }
        }
        
        # Mock the save_entity function to avoid file I/O
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "message": "Entity saved successfully",
                "data": {
                    "id": "test-123",
                    "data": link_config["data"],  # Will contain rendered data after fix
                    "metadata": link_config["metadata"],
                    "timestamp": "2026-01-04T12:00:00"
                }
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert - Check what was passed to save_entity
            assert mock_save.called, "save_entity should be called"
            call_args = mock_save.call_args
            saved_data = call_args[0][1]  # Second positional arg is 'data'
            
            # The bug: templates should be rendered BEFORE saving
            assert saved_data["simple_field"] == "rendered_value", \
                f"Expected 'rendered_value' but got '{saved_data['simple_field']}'"
            assert saved_data["literal_field"] == "no template here"
            # Ensure templates are NOT in the saved data
            assert "{{" not in str(saved_data), \
                f"Template strings should be rendered, but found in: {saved_data}"
    
    def test_storage_save_renders_nested_template_strings(self):
        """Test that template strings in nested dict values are rendered"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "simple_field": "{{ TestLink.data.value }}",
                "nested_field": "{{ TestLink.data.nested.value }}",
                "literal_field": "no template here"
            },
            "metadata": {
                "source": "test"
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "value": "rendered_value",
                    "nested": {
                        "value": "nested_rendered_value"
                    }
                },
                "raw": "raw content"
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "message": "Entity saved successfully",
                "data": {
                    "id": "test-123",
                    "data": link_config["data"],
                    "metadata": link_config["metadata"],
                    "timestamp": "2026-01-04T12:00:00"
                }
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert
            assert mock_save.called
            saved_data = mock_save.call_args[0][1]
            
            assert saved_data["simple_field"] == "rendered_value"
            assert saved_data["nested_field"] == "nested_rendered_value"
            assert saved_data["literal_field"] == "no template here"
            assert "{{" not in str(saved_data)
    
    def test_storage_save_renders_deeply_nested_dicts(self):
        """Test that templates in deeply nested dictionaries are rendered"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "level1": {
                    "level2": {
                        "template_field": "{{ TestLink.data.deep_value }}",
                        "literal_field": "literal"
                    }
                }
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "deep_value": "deep_rendered_value"
                }
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "data": {"id": "test-123"}
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert
            saved_data = mock_save.call_args[0][1]
            assert saved_data["level1"]["level2"]["template_field"] == "deep_rendered_value"
            assert saved_data["level1"]["level2"]["literal_field"] == "literal"
    
    def test_storage_save_handles_lists_with_templates(self):
        """Test that templates in list values are rendered"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "items": [
                    "{{ TestLink.data.item1 }}",
                    "literal_item",
                    "{{ TestLink.data.item2 }}"
                ]
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "item1": "rendered_item1",
                    "item2": "rendered_item2"
                }
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "data": {"id": "test-123"}
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert
            saved_data = mock_save.call_args[0][1]
            assert saved_data["items"][0] == "rendered_item1"
            assert saved_data["items"][1] == "literal_item"
            assert saved_data["items"][2] == "rendered_item2"
    
    def test_storage_save_preserves_non_string_values(self):
        """Test that non-string values (numbers, booleans, None) are preserved"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "number": 42,
                "boolean": True,
                "null_value": None,
                "template": "{{ TestLink.data.value }}"
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "value": "rendered"
                }
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "data": {"id": "test-123"}
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert
            saved_data = mock_save.call_args[0][1]
            assert saved_data["number"] == 42
            assert saved_data["boolean"] is True
            assert saved_data["null_value"] is None
            assert saved_data["template"] == "rendered"
    
    def test_storage_save_handles_undefined_variables(self):
        """Test behavior when template references undefined variables"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "undefined_field": "{{ UndefinedLink.data.value }}"
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "value": "exists"
                }
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "data": {"id": "test-123"}
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert - undefined variables should render as empty string
            # or raise an exception depending on Jinja2 configuration
            saved_data = mock_save.call_args[0][1]
            # With default Jinja2, undefined variables render as empty string
            assert saved_data["undefined_field"] == ""
    
    def test_storage_save_handles_malformed_templates(self):
        """Test behavior with malformed template syntax"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "malformed": "{{ TestLink.data.value }",  # Missing closing braces
                "normal": "{{ TestLink.data.value }}"
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "value": "rendered"
                }
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "data": {"id": "test-123"}
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert - malformed templates should be left as-is
            saved_data = mock_save.call_args[0][1]
            assert saved_data["malformed"] == "{{ TestLink.data.value }"  # Unchanged
            assert saved_data["normal"] == "rendered"
    
    def test_extract_data_recursively_renders_nested_structures(self):
        """Test the _extract_data method directly for recursive rendering"""
        # Arrange
        data_source = {
            "simple": "{{ Link1.data.value }}",
            "nested": {
                "deep": "{{ Link2.data.nested_value }}",
                "list": [
                    "{{ Link3.data.item1 }}",
                    "literal"
                ]
            }
        }
        
        context = {
            "Link1": {"data": {"value": "rendered1"}},
            "Link2": {"data": {"nested_value": "rendered2"}},
            "Link3": {"data": {"item1": "rendered3"}}
        }
        
        # Act
        result = StorageSaveLink._extract_data(data_source, context)
        
        # Assert
        assert result["simple"] == "rendered1"
        assert result["nested"]["deep"] == "rendered2"
        assert result["nested"]["list"][0] == "rendered3"
        assert result["nested"]["list"][1] == "literal"
    
    def test_storage_save_renders_metadata_templates(self):
        """Test that template strings in metadata are also rendered"""
        # Arrange
        link_config = {
            "collection": "test_collection",
            "data": {
                "field": "{{ TestLink.data.value }}"
            },
            "metadata": {
                "source": "test",
                "user": "{{ TestLink.data.user }}",
                "timestamp": "{{ TestLink.data.time }}"
            }
        }
        
        context = {
            "TestLink": {
                "data": {
                    "value": "test_value",
                    "user": "alice",
                    "time": "2026-01-04T12:00:00"
                }
            }
        }
        
        # Mock the save_entity function
        with patch('core.domains.storage.links.save_entity') as mock_save:
            mock_save.return_value = {
                "success": True,
                "data": {"id": "test-123"}
            }
            
            # Act
            result = StorageSaveLink.execute(link_config, context)
            
            # Assert - Check metadata was rendered
            assert mock_save.called
            saved_metadata = mock_save.call_args[0][2]  # Third positional arg is 'metadata'
            assert saved_metadata["source"] == "test"
            assert saved_metadata["user"] == "alice"
            assert saved_metadata["timestamp"] == "2026-01-04T12:00:00"
            assert "{{" not in str(saved_metadata)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
