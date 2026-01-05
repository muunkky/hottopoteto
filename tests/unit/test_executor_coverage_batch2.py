"""Additional executor tests for 100% coverage - BATCH 2"""
import pytest
import yaml
from core.executor import (
    RecipeExecutor,
    RecipeLinkOutput,
    LLMOutput,
    FunctionOutput,
    TerminateProcessException
)


class TestProcessFunctionInputs:
    """Test _process_function_inputs method."""
    
    def test_no_inputs_returns_empty_dict(self, tmp_path):
        """Test function with no inputs."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        link = {"name": "test_func"}
        
        inputs = executor._process_function_inputs(link)
        
        assert inputs == {}
    
    def test_static_value_inputs(self, tmp_path):
        """Test function with static value inputs."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        link = {
            "name": "test_func",
            "inputs": {
                "param1": 42,
                "param2": "hello",
                "param3": True
            }
        }
        
        inputs = executor._process_function_inputs(link)
        
        assert inputs["param1"] == 42
        assert inputs["param2"] == "hello"
        assert inputs["param3"] is True
    
    def test_dict_input_with_value(self, tmp_path):
        """Test input as dict with 'value' key."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        link = {
            "name": "test_func",
            "inputs": {
                "param": {"value": 100}
            }
        }
        
        inputs = executor._process_function_inputs(link)
        
        assert inputs["param"] == 100
    
    def test_dict_input_with_default(self, tmp_path):
        """Test input as dict with 'default' key."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        link = {
            "name": "test_func",
            "inputs": {
                "param": {"default": "default_value"}
            }
        }
        
        inputs = executor._process_function_inputs(link)
        
        assert inputs["param"] == "default_value"


class TestBuildContextConversions:
    """Test build_context with various data types."""
    
    def test_build_context_with_recipe_link_output(self, tmp_path):
        """Test context from RecipeLinkOutput object."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        memory = {
            "test": RecipeLinkOutput(raw="raw text", data={"key": "value"})
        }
        
        context = executor.build_context(memory)
        
        assert context["test"]["raw"] == "raw text"
        assert context["test"]["data"] == {"key": "value"}
    
    def test_build_context_with_dict_containing_raw_and_data(self, tmp_path):
        """Test context from dict with raw and data keys."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        memory = {
            "test": {"raw": "test raw", "data": {"num": 42}}
        }
        
        context = executor.build_context(memory)
        
        assert context["test"]["raw"] == "test raw"
        assert context["test"]["data"] == {"num": 42}
    
    def test_build_context_with_plain_dict(self, tmp_path):
        """Test context from plain dictionary."""
        recipe_file = tmp_path / "test.yaml"
        recipe_data = {"links": []}
        recipe_file.write_text(yaml.dump(recipe_data))
        
        executor = RecipeExecutor(str(recipe_file))
        memory = {
            "test": {"result": "value", "count": 5}
        }
        
        context = executor.build_context(memory)
        
        assert "test" in context
        assert context["test"]["data"] == {"result": "value", "count": 5}


class TestTerminateProcessException:
    """Test TerminateProcessException."""
    
    def test_exception_creation(self):
        """Test creating TerminateProcessException."""
        exc = TerminateProcessException()
        assert exc.message == "Process terminated by function"
    
    def test_exception_with_custom_message(self):
        """Test creating exception with custom message."""
        exc = TerminateProcessException("Custom termination message")
        assert exc.message == "Custom termination message"
    
    def test_exception_is_exception(self):
        """Test that it's an Exception subclass."""
        exc = TerminateProcessException()
        assert isinstance(exc, Exception)


class TestOutputModelsInheritance:
    """Test output model inheritance."""
    
    def test_llm_output_inherits_from_recipe_link_output(self):
        """Test LLMOutput is subclass of RecipeLinkOutput."""
        output = LLMOutput(data={"test": "value"})
        assert isinstance(output, RecipeLinkOutput)
    
    def test_function_output_inherits_from_recipe_link_output(self):
        """Test FunctionOutput is subclass of RecipeLinkOutput."""
        output = FunctionOutput(data={"result": 100})
        assert isinstance(output, RecipeLinkOutput)
    
    def test_llm_output_get_data_method(self):
        """Test LLMOutput has get_data method."""
        output = LLMOutput(data={"answer": "42"})
        result = output.get_data()
        assert result == {"answer": "42"}
    
    def test_function_output_get_data_method(self):
        """Test FunctionOutput has get_data method."""
        output = FunctionOutput(data={"value": 999})
        result = output.get_data()
        assert result == {"value": 999}


class TestFunctionRegistryGlobal:
    """Test global FunctionRegistry operations."""
    
    def setup_method(self):
        """Clear registry."""
        from core.executor import FunctionRegistry
        FunctionRegistry._functions = {}
    
    def test_register_multiple_functions(self):
        """Test registering multiple functions."""
        from core.executor import FunctionRegistry
        
        def func1():
            return 1
        def func2():
            return 2
        def func3():
            return 3
        
        FunctionRegistry.register("f1", func1)
        FunctionRegistry.register("f2", func2)
        FunctionRegistry.register("f3", func3)
        
        assert len(FunctionRegistry._functions) == 3
        assert FunctionRegistry.get("f1")() == 1
        assert FunctionRegistry.get("f2")() == 2
        assert FunctionRegistry.get("f3")() == 3
    
    def test_register_overwrites_existing(self):
        """Test that re-registering overwrites."""
        from core.executor import FunctionRegistry
        
        def old_func():
            return "old"
        def new_func():
            return "new"
        
        FunctionRegistry.register("test", old_func)
        FunctionRegistry.register("test", new_func)
        
        assert FunctionRegistry.get("test")() == "new"
    
    def test_register_with_different_metadata(self):
        """Test registering with various metadata."""
        from core.executor import FunctionRegistry
        
        def func():
            return True
        
        meta = {
            "description": "Test function",
            "params": ["a", "b"],
            "returns": "bool"
        }
        
        FunctionRegistry.register("test", func, meta)
        
        assert FunctionRegistry._functions["test"]["metadata"] == meta
