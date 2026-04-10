"""Tests for core.templates module."""
import pytest
import os
from core.templates import (
    register_template_directory,
    get_template_directories,
    resolve_template_path,
    list_templates,
    _template_directories
)


class TestTemplateDirectoryRegistry:
    """Tests for template directory registration."""
    
    def setup_method(self):
        """Reset template directories before each test."""
        _template_directories.clear()
        _template_directories["text"] = ["templates/text"]
        _template_directories["recipes"] = ["templates/recipes"]
    
    def test_register_new_template_type(self):
        """Test registering a new template type."""
        register_template_directory("custom", "plugins/custom/templates")
        
        assert "custom" in _template_directories
        assert "plugins/custom/templates" in _template_directories["custom"]
        assert "templates/custom" in _template_directories["custom"]  # Default added
    
    def test_register_additional_directory_for_existing_type(self):
        """Test adding another directory to existing template type."""
        register_template_directory("text", "plugins/extra/text")
        
        assert "plugins/extra/text" in _template_directories["text"]
        assert "templates/text" in _template_directories["text"]  # Original still there
    
    def test_register_duplicate_directory_ignored(self):
        """Test that registering same directory twice doesn't duplicate."""
        register_template_directory("text", "plugins/test/text")
        register_template_directory("text", "plugins/test/text")
        
        count = _template_directories["text"].count("plugins/test/text")
        assert count == 1
    
    def test_get_template_directories_returns_list(self):
        """Test getting directories for a template type."""
        register_template_directory("recipes", "plugins/custom/recipes")
        
        dirs = get_template_directories("recipes")
        
        assert isinstance(dirs, list)
        assert "templates/recipes" in dirs
        assert "plugins/custom/recipes" in dirs
    
    def test_get_template_directories_unknown_type_returns_empty(self):
        """Test getting directories for non-existent type returns empty list."""
        dirs = get_template_directories("nonexistent")
        
        assert dirs == []
    
    def test_default_template_directories_exist(self):
        """Test that default text and recipes directories are registered."""
        text_dirs = get_template_directories("text")
        recipe_dirs = get_template_directories("recipes")
        
        assert "templates/text" in text_dirs
        assert "templates/recipes" in recipe_dirs


class TestResolveTemplatePath:
    """Tests for template path resolution."""
    
    def test_resolve_existing_direct_path(self, tmp_path):
        """Test resolving a direct file path that exists."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = resolve_template_path(str(test_file))
        
        assert result == str(test_file)
    
    def test_resolve_nonexistent_direct_path_returns_none(self):
        """Test that non-existent direct path returns None."""
        result = resolve_template_path("/nonexistent/path/file.txt")
        
        assert result is None
    
    def test_resolve_returns_none_for_missing_template(self):
        """Test that missing template reference returns None."""
        result = resolve_template_path("domain.nonexistent")
        
        assert result is None
    
    def test_resolve_with_file_extension_in_reference(self):
        """Test resolving template with extension in reference."""
        # This would only work if the file actually exists
        result = resolve_template_path("test.txt")
        
        # Should return None since file doesn't exist in test environment
        assert result is None or os.path.exists(result)


class TestListTemplates:
    """Tests for template listing functionality."""
    
    def test_list_templates_returns_dict(self):
        """Test that list_templates returns a dictionary."""
        result = list_templates()
        
        assert isinstance(result, dict)
    
    def test_list_templates_with_type_filter(self):
        """Test listing templates filtered by type."""
        result = list_templates(template_type="text")
        
        assert isinstance(result, dict)
        # Result structure depends on what files actually exist
    
    def test_list_templates_without_filter(self):
        """Test listing all templates across all types."""
        result = list_templates()
        
        assert isinstance(result, dict)
        # Should include entries for registered template types
