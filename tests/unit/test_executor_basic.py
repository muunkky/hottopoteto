"""Simple focused tests for executor.py to boost coverage."""
import pytest
import os
import yaml
import json
from pathlib import Path
from core.executor import (
    RecipeLinkOutput,
    LLMOutput,
    FunctionOutput,
    UserInputOutput,
    RecipeExecutor,
    FunctionRegistry,
    extract_json,
    attempt_fix_truncated_json
)


class TestFunctionRegistry:
    """Tests for function registry."""
    
    def setup_method(self):
        """Clear registry."""
        FunctionRegistry._functions = {}
    
    def test_register_function(self):
        """Test registering a function."""
        def test_func():
            return 42
        
        FunctionRegistry.register("test", test_func)
        
        assert "test" in FunctionRegistry._functions
        result = FunctionRegistry.get("test")
        assert result() == 42
    
    def test_register_with_metadata(self):
        """Test registering function with metadata."""
        def test_func():
            return "hello"
        
        meta = {"description": "Test function"}
        FunctionRegistry.register("test", test_func, meta)
        
        assert FunctionRegistry._functions["test"]["metadata"] == meta
    
    def test_get_nonexistent_returns_none(self):
        """Test getting non-existent function."""
        result = FunctionRegistry.get("nonexistent")
        assert result is None
    
    def test_get_returns_function(self):
        """Test that get returns callable."""
        def my_func(x):
            return x * 2
        
        FunctionRegistry.register("double", my_func)
        func = FunctionRegistry.get("double")
        
        assert callable(func)
        assert func(5) == 10


class TestRecipeLinkOutput:
    """Tests for output model."""
    
    def test_create_output_with_raw_and_data(self):
        """Test creating output with raw and data."""
        output = RecipeLinkOutput(
            raw="test output",
            data={"key": "value"}
        )
        
        assert output.raw == "test output"
        assert output.data == {"key": "value"}
    
    def test_create_output_minimal(self):
        """Test creating output with defaults."""
        output = RecipeLinkOutput()
        
        assert output.raw is None
        assert output.data == {}
    
    def test_get_data_returns_data(self):
        """Test get_data returns data field."""
        output = RecipeLinkOutput(data={"result": 42})
        result = output.get_data()
        assert result == {"result": 42}
    
    def test_get_data_falls_back_to_raw(self):
        """Test get_data parses raw JSON."""
        output = RecipeLinkOutput(raw='{"value": 123}')
        result = output.get_data()
        assert result == {"value": 123}
    
    def test_get_data_wraps_unparseable_raw(self):
        """Test get_data wraps non-JSON raw."""
        output = RecipeLinkOutput(raw="plain text")
        result = output.get_data()
        assert result == {"raw_content": "plain text"}


class TestLLMOutput:
    """Tests for LLM output model."""
    
    def test_create_llm_output(self):
        """Test creating LLM output."""
        output = LLMOutput(raw="response", data={"answer": "yes"})
        assert output.raw == "response"
        assert output.data == {"answer": "yes"}


class TestFunctionOutput:
    """Tests for function output model."""
    
    def test_create_function_output(self):
        """Test creating function output."""
        output = FunctionOutput(data={"result": 100})
        assert output.data == {"result": 100}


class TestUserInputOutput:
    """Tests for user input output model."""
    
    def test_create_user_input_output(self):
        """Test creating user input output."""
        output = UserInputOutput(data={"input": "user text"})
        assert output.data == {"input": "user text"}


class TestAttemptFixTruncatedJson:
    """Tests for truncated JSON fixing."""
    
    def test_adds_closing_brace(self):
        """Test adding missing closing brace."""
        text = '{"name": "test", "value": 42'
        result = attempt_fix_truncated_json(text)
        assert result.endswith("}")
    
    def test_handles_already_complete_json(self):
        """Test with complete JSON."""
        text = '{"complete": true}'
        result = attempt_fix_truncated_json(text)
        assert "complete" in result
    
    def test_extracts_between_braces(self):
        """Test extraction between first { and last }."""
        text = 'prefix {"data": "value"} suffix'
        result = attempt_fix_truncated_json(text)
        assert "{" in result
        assert "data" in result
    
    def test_handles_no_opening_brace(self):
        """Test with no opening brace."""
        text = "no json here"
        result = attempt_fix_truncated_json(text)
        assert result == text
    
    def test_adds_multiple_closing_braces(self):
        """Test adding multiple missing closing braces."""
        text = '{{"nested": {"deep": "value"'
        result = attempt_fix_truncated_json(text)
        assert result.count("}") >= 2


class TestExtractJsonSimple:
    """Simple tests for extract_json focusing on coverage."""
    
    def test_extract_plain_json_object(self):
        """Test extracting plain JSON object."""
        text = '{"key": "value", "number": 123}'
        result = extract_json(text)
        assert '{"key": "value", "number": 123}' in result
    
    def test_extract_json_from_markdown(self):
        """Test extracting JSON from markdown code block."""
        text = '''Here is the data:
```json
{"name": "test", "value": 42}
```
'''
        result = extract_json(text)
        assert "name" in result
        assert "test" in result
    
    def test_extract_json_array(self):
        """Test extracting JSON array."""
        text = '[1, 2, 3, 4, 5]'
        result = extract_json(text)
        assert "[1, 2, 3, 4, 5]" == result
    
    def test_extract_json_with_text_before(self):
        """Test extracting JSON when text before it."""
        text = 'Some text {"data": "value"} more text'
        result = extract_json(text)
        assert "data" in result
    
    def test_extract_returns_original_if_no_json(self):
        """Test that non-JSON text is returned as-is."""
        text = "This is plain text with no JSON"
        result = extract_json(text)
        assert result == text


class TestAttemptFixTruncatedJson:
    """Tests for truncated JSON fixing."""
    
    def test_adds_closing_brace(self):
        """Test adding missing closing brace."""
        text = '{"name": "test", "value": 42'
        result = attempt_fix_truncated_json(text)
        assert result.endswith("}")
    
    def test_handles_already_complete_json(self):
        """Test with complete JSON."""
        text = '{"complete": true}'
        result = attempt_fix_truncated_json(text)
        assert "complete" in result


class TestRecipeExecutorInit:
    """Tests for RecipeExecutor initialization."""
    
    def test_init_with_valid_recipe(self, tmp_path):
        """Test initializing with valid recipe file."""
        recipe_file = tmp_path / "test_recipe.yaml"
        recipe_data = {
            "domain": "llm",
            "links": [
                {"name": "test_link", "type": "gemini", "prompt": "test"}
            ]
        }
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert executor.domain == "llm"
        assert executor.recipe["domain"] == "llm"
        assert len(executor.recipe["links"]) == 1
    
    def test_init_with_default_domain(self, tmp_path):
        """Test that domain defaults to 'generic'."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert executor.domain == "generic"
    
    def test_init_with_explicit_domain(self, tmp_path):
        """Test specifying domain explicitly."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"domain": "storage", "links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file), domain="llm")
        
        # Explicit domain overrides recipe domain
        assert executor.domain == "llm"
    
    def test_init_creates_jinja_environment(self, tmp_path):
        """Test that initialization sets up Jinja environment."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert hasattr(executor, "env")
        assert executor.env is not None
    
    def test_init_creates_memory_dict(self, tmp_path):
        """Test that memory is initialized."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert hasattr(executor, "memory")
        assert isinstance(executor.memory, dict)
    
    def test_init_creates_function_registry(self, tmp_path):
        """Test that function registry is initialized."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert hasattr(executor, "function_registry")
        assert "random_number" in executor.function_registry


class TestRecipeExecutorBuildContext:
    """Tests for build_context method."""
    
    def test_build_empty_context(self, tmp_path):
        """Test building context with no history."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        context = executor.build_context({})
        
        assert isinstance(context, dict)
    
    def test_build_context_with_memory(self, tmp_path):
        """Test building context from memory."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        memory = {
            "link1": RecipeLinkOutput(raw="test", data={"value": 1})
        }
        
        context = executor.build_context(memory)
        
        assert "link1" in context
        assert context["link1"]["data"] == {"value": 1}
        assert context["link1"]["raw"] == "test"
    
    def test_build_context_with_dict_memory(self, tmp_path):
        """Test building context with dictionary memory."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        memory = {
            "link1": {"raw": "test", "data": {"num": 42}}
        }
        
        context = executor.build_context(memory)
        
        assert "link1" in context
        assert context["link1"]["raw"] == "test"
        assert context["link1"]["data"] == {"num": 42}


class TestRecipeExecutorMemory:
    """Tests for memory management."""
    
    def test_memory_initialized_as_dict(self, tmp_path):
        """Test memory is initialized as dict."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert isinstance(executor.memory, dict)
    
    def test_can_store_in_memory(self, tmp_path):
        """Test storing values in memory."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        executor.memory["test_key"] = "test_value"
        
        assert "test_key" in executor.memory
        assert executor.memory["test_key"] == "test_value"
    
    def test_can_retrieve_from_memory(self, tmp_path):
        """Test retrieving values from memory."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        executor.memory["my_key"] = {"data": "my_value"}
        
        result = executor.memory.get("my_key")
        
        assert result == {"data": "my_value"}


class TestRecipeExecutorFunctionRandom:
    """Test the built-in random_number function."""
    
    def test_random_number_function_exists(self, tmp_path):
        """Test random_number function is registered."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        
        assert "random_number" in executor.function_registry
    
    def test_random_number_function_returns_dict(self, tmp_path):
        """Test random_number returns dict with num_events."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        result = executor.function_registry["random_number"]()
        
        assert isinstance(result, dict)
        assert "num_events" in result
        assert isinstance(result["num_events"], int)
    
    def test_random_number_within_range(self, tmp_path):
        """Test random_number respects min/max."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        result = executor.function_registry["random_number"](min_value=10, max_value=20)
        
        assert 10 <= result["num_events"] <= 20
    
    def test_random_number_default_range(self, tmp_path):
        """Test random_number with default range."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        result = executor.function_registry["random_number"]()
        
        assert 1 <= result["num_events"] <= 3

