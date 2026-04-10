"""Additional executor tests for 100% coverage - BATCH 1"""
import pytest
import yaml
import json
from core.executor import (
    RecipeExecutor,
    extract_json,
    FunctionRegistry,
    FunctionOutput,
    LLMOutput,
    RecipeLinkOutput
)


class TestExtractJsonEdgeCases:
    """Test extract_json with various edge cases."""
    
    def test_json_with_markdown_fences_labeled(self):
        """Extract JSON from labeled markdown block."""
        text = "```json\n{\"key\": \"value\"}\n```"
        result = extract_json(text)
        data = json.loads(result)
        assert data == {"key": "value"}
    
    def test_json_with_unlabeled_markdown_fences(self):
        """Extract JSON from unlabeled markdown block."""
        text = "```\n{\"data\": 123}\n```"
        result = extract_json(text)
        data = json.loads(result)
        assert data == {"data": 123}
    
    def test_json_array_extraction(self):
        """Extract JSON array."""
        text = "Some text [1, 2, 3] more text"
        result = extract_json(text)
        data = json.loads(result)
        assert data == [1, 2, 3]
    
    def test_nested_json_extraction(self):
        """Extract nested JSON."""
        text = '{"outer": {"inner": {"value": 42}}}'
        result = extract_json(text)
        data = json.loads(result)
        assert data["outer"]["inner"]["value"] == 42
    
    def test_json_with_escaped_quotes(self):
        """Extract JSON with escaped quotes."""
        text = '{"message": "He said \\"hello\\""}'
        result = extract_json(text)
        data = json.loads(result)
        assert '"hello"' in data["message"]
    
    def test_json_with_newlines(self):
        """Extract multi-line JSON."""
        text = '''{\n  "line1": "value1",\n  "line2": "value2"\n}'''
        result = extract_json(text)
        data = json.loads(result)
        assert data == {"line1": "value1", "line2": "value2"}
    
    def test_json_with_numbers(self):
        """Extract JSON with various number types."""
        text = '{"int": 42, "float": 3.14, "negative": -5}'
        result = extract_json(text)
        data = json.loads(result)
        assert data["int"] == 42
        assert data["float"] == 3.14
        assert data["negative"] == -5
    
    def test_json_with_booleans(self):
        """Extract JSON with boolean values."""
        text = '{"true_val": true, "false_val": false}'
        result = extract_json(text)
        data = json.loads(result)
        assert data["true_val"] is True
        assert data["false_val"] is False
    
    def test_json_with_null(self):
        """Extract JSON with null value."""
        text = '{"value": null}'
        result = extract_json(text)
        data = json.loads(result)
        assert data["value"] is None
    
    def test_json_empty_object(self):
        """Extract empty JSON object."""
        text = "{}"
        result = extract_json(text)
        data = json.loads(result)
        assert data == {}
    
    def test_json_empty_array(self):
        """Extract empty JSON array."""
        text = "[]"
        result = extract_json(text)
        data = json.loads(result)
        assert data == []
    
    def test_multiple_json_objects_returns_first(self):
        """When multiple JSON objects, extract first."""
        text = '{"first": 1} {"second": 2}'
        result = extract_json(text)
        data = json.loads(result)
        assert "first" in data


class TestRecipeExecutorEdgeCases:
    """Test RecipeExecutor edge cases."""
    
    def test_init_with_list_links(self, tmp_path):
        """Test recipe with links as list."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {
            "links": [
                {"name": "link1", "type": "function"},
                {"name": "link2", "type": "function"}
            ]
        }
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        assert len(executor.recipe["links"]) == 2
    
    def test_init_with_dict_links(self, tmp_path):
        """Test recipe with links as dictionary."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {
            "links": {
                "link1": {"type": "function"},
                "link2": {"type": "function"}
            }
        }
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        assert len(executor.recipe["links"]) == 2
    
    def test_memory_stores_link_outputs(self, tmp_path):
        """Test that memory can store link outputs."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        executor.memory["link1"] = FunctionOutput(data={"result": 42})
        
        assert "link1" in executor.memory
        assert executor.memory["link1"].data == {"result": 42}
    
    def test_build_context_handles_multiple_links(self, tmp_path):
        """Test building context from multiple memory entries."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        memory = {
            "link1": RecipeLinkOutput(data={"value": 1}),
            "link2": RecipeLinkOutput(data={"value": 2}),
            "link3": RecipeLinkOutput(data={"value": 3})
        }
        
        context = executor.build_context(memory)
        
        assert len(context) == 3
        assert "link1" in context
        assert "link2" in context
        assert "link3" in context
    
    def test_function_registry_attribute_exists(self, tmp_path):
        """Test that function_registry is set up."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert hasattr(executor, "function_registry")
        assert isinstance(executor.function_registry, dict)
    
    def test_recipe_path_attribute(self, tmp_path):
        """Test that recipe_path is stored."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert executor.recipe_path == str(recipe_file)
    
    def test_env_attribute_is_jinja_environment(self, tmp_path):
        """Test that env is a Jinja Environment."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        from jinja2 import Environment
        assert isinstance(executor.env, Environment)
    
    def test_random_number_function_callable(self, tmp_path):
        """Test that random_number function is callable."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        func = executor.function_registry["random_number"]
        
        assert callable(func)
        result = func()
        assert isinstance(result, dict)
        assert "num_events" in result
