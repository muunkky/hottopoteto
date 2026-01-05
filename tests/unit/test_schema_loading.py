"""
Tests for external schema file loading.

Part of DOCENRICH Sprint - Step 2: External Schema File Loading.

TDD approach: Write failing tests first, then implement.
"""
import pytest
import os
import yaml
import json
from unittest.mock import patch, MagicMock


class TestSchemaFileLoading:
    """Tests for loading JSON Schema files from templates/schemas/."""
    
    @pytest.fixture
    def sample_schema_yaml(self, tmp_path):
        """Create a sample schema YAML file."""
        schema_dir = tmp_path / "templates" / "schemas"
        schema_dir.mkdir(parents=True)
        
        schema = {
            "type": "object",
            "properties": {
                "english_word": {"type": "string", "description": "The English word"},
                "translation": {"type": "string", "description": "The translation"},
                "origin_words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {"type": "string"},
                            "meaning": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["english_word", "translation"]
        }
        
        schema_file = schema_dir / "test_word.yaml"
        with open(schema_file, 'w') as f:
            yaml.dump(schema, f)
        
        return schema_file
    
    @pytest.fixture
    def sample_schema_json(self, tmp_path):
        """Create a sample schema JSON file."""
        schema_dir = tmp_path / "templates" / "schemas"
        schema_dir.mkdir(parents=True, exist_ok=True)
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        schema_file = schema_dir / "simple.json"
        with open(schema_file, 'w') as f:
            json.dump(schema, f)
        
        return schema_file


class TestSchemaDirectoryRegistration:
    """Tests for registering schema template directories."""
    
    def test_schema_directory_registered_by_default(self):
        """Schema directory should be registered alongside text templates."""
        from core.templates import get_template_directories
        
        # schemas should be a registered template type
        schema_dirs = get_template_directories("schemas")
        assert len(schema_dirs) > 0, "No schema directories registered"
        assert any("schemas" in d for d in schema_dirs), "Default schemas directory not found"
    
    def test_can_register_plugin_schema_directory(self):
        """Plugins should be able to register additional schema directories."""
        from core.templates import register_template_directory, get_template_directories
        
        # Register a plugin schema directory
        register_template_directory("schemas", "plugins/conlang/schemas")
        
        schema_dirs = get_template_directories("schemas")
        assert "plugins/conlang/schemas" in schema_dirs


class TestSchemaResolution:
    """Tests for resolving schema file references."""
    
    def test_resolve_schema_from_file_reference(self, sample_schema_yaml, tmp_path):
        """Schema can be loaded from file: reference."""
        from core.templates import resolve_template_path
        
        # Mock the template directories
        with patch('core.templates._template_directories', {
            "schemas": [str(tmp_path / "templates" / "schemas")]
        }):
            path = resolve_template_path("test_word.yaml")
            assert path is not None
            assert os.path.exists(path)
    
    def test_resolve_schema_supports_yaml_extension(self, sample_schema_yaml, tmp_path):
        """Schema resolution should support .yaml extension."""
        from core.templates import resolve_template_path
        
        with patch('core.templates._template_directories', {
            "schemas": [str(tmp_path / "templates" / "schemas")]
        }):
            # Should find test_word.yaml
            path = resolve_template_path("test_word.yaml")
            assert path is not None
            assert path.endswith(".yaml")
    
    def test_resolve_schema_supports_json_extension(self, sample_schema_json, tmp_path):
        """Schema resolution should support .json extension."""
        from core.templates import resolve_template_path
        
        with patch('core.templates._template_directories', {
            "schemas": [str(tmp_path / "templates" / "schemas")]
        }):
            path = resolve_template_path("simple.json")
            assert path is not None
            assert path.endswith(".json")


class TestSchemaLoading:
    """Tests for actually loading and parsing schema files."""
    
    def test_load_yaml_schema_file(self, sample_schema_yaml):
        """Should load and parse YAML schema file."""
        from core.schemas import load_schema_file
        
        schema = load_schema_file(str(sample_schema_yaml))
        
        assert schema is not None
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "english_word" in schema["properties"]
    
    def test_load_json_schema_file(self, sample_schema_json):
        """Should load and parse JSON schema file."""
        from core.schemas import load_schema_file
        
        schema = load_schema_file(str(sample_schema_json))
        
        assert schema is not None
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
    
    def test_load_schema_validates_structure(self, tmp_path):
        """Should validate that loaded file is a valid JSON Schema."""
        from core.schemas import load_schema_file, SchemaValidationError
        
        # Create an invalid schema file
        schema_dir = tmp_path / "templates" / "schemas"
        schema_dir.mkdir(parents=True)
        
        invalid_file = schema_dir / "invalid.yaml"
        with open(invalid_file, 'w') as f:
            yaml.dump({"not_a_valid_schema": True}, f)
        
        # Should raise validation error
        with pytest.raises(SchemaValidationError):
            load_schema_file(str(invalid_file))
    
    def test_load_schema_file_not_found(self):
        """Should raise clear error for missing schema file."""
        from core.schemas import load_schema_file, SchemaNotFoundError
        
        with pytest.raises(SchemaNotFoundError):
            load_schema_file("/nonexistent/schema.yaml")
    
    def test_load_schema_caches_result(self, sample_schema_yaml):
        """Schema files should be cached to avoid repeated disk reads."""
        from core.schemas import load_schema_file, clear_schema_cache
        
        # Clear any existing cache
        clear_schema_cache()
        
        # Load twice
        schema1 = load_schema_file(str(sample_schema_yaml))
        schema2 = load_schema_file(str(sample_schema_yaml))
        
        # Should return the same object (cached)
        assert schema1 is schema2


class TestResolveSchemaReference:
    """Tests for resolving schema references in recipe configuration."""
    
    def test_resolve_file_reference(self, sample_schema_yaml, tmp_path):
        """Should resolve { file: 'path' } reference to loaded schema."""
        from core.schemas import resolve_schema_reference
        
        with patch('core.templates.get_template_directories', return_value=[
            str(tmp_path / "templates" / "schemas")
        ]):
            schema_ref = {"file": "test_word.yaml"}
            schema = resolve_schema_reference(schema_ref)
            
            assert schema is not None
            assert schema["type"] == "object"
    
    def test_resolve_inline_schema(self):
        """Should pass through inline schema definitions unchanged."""
        from core.schemas import resolve_schema_reference
        
        inline_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}}
        }
        
        result = resolve_schema_reference(inline_schema)
        
        assert result == inline_schema
    
    def test_resolve_nested_file_path(self, tmp_path):
        """Should resolve nested paths like 'domain/schema.yaml'."""
        from core.schemas import resolve_schema_reference
        
        # Create nested schema
        schema_dir = tmp_path / "templates" / "schemas" / "conlang"
        schema_dir.mkdir(parents=True)
        
        schema = {"type": "object", "properties": {"word": {"type": "string"}}}
        schema_file = schema_dir / "eldorian_word.yaml"
        with open(schema_file, 'w') as f:
            yaml.dump(schema, f)
        
        with patch('core.templates.get_template_directories', return_value=[
            str(tmp_path / "templates" / "schemas")
        ]):
            schema_ref = {"file": "conlang/eldorian_word.yaml"}
            result = resolve_schema_reference(schema_ref)
            
            assert result is not None
            assert result["type"] == "object"


class TestExecutorSchemaIntegration:
    """Integration tests for executor using schema file references."""
    
    def test_executor_resolves_schema_in_link(self, tmp_path):
        """Executor should resolve schema file references in link configs."""
        # This tests the full integration path
        # When a link config has schema: { file: "path" },
        # the executor should load and use that schema
        
        # Create test schema
        schema_dir = tmp_path / "templates" / "schemas"
        schema_dir.mkdir(parents=True)
        
        schema = {"type": "object", "properties": {"result": {"type": "string"}}}
        schema_file = schema_dir / "test_output.yaml"
        with open(schema_file, 'w') as f:
            yaml.dump(schema, f)
        
        # Create test recipe
        recipe_dir = tmp_path / "templates" / "recipes"
        recipe_dir.mkdir(parents=True)
        
        recipe = {
            "name": "test_schema_recipe",
            "domain": "generic",
            "links": [
                {
                    "name": "Test",
                    "type": "llm",
                    "prompt": "Say hello",
                    "output_schema": {"file": "test_output.yaml"}
                }
            ]
        }
        
        recipe_file = recipe_dir / "test_recipe.yaml"
        with open(recipe_file, 'w') as f:
            yaml.dump(recipe, f)
        
        # TODO: Test executor integration after implementing schema resolution
        # This is a placeholder for the integration test
        pytest.skip("Integration test - implement after core.schemas module exists")
