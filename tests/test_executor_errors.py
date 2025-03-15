import os
import pytest
from core.executor import RecipeExecutor, TerminateProcessException
import yaml

# Fixture for a temporary directory
@pytest.fixture
def temp_dir(tmpdir):
    yield tmpdir

def test_recipe_executor_invalid_yaml(temp_dir):
    """Test executing a recipe with an invalid YAML file."""
    recipe_path = os.path.join(temp_dir, "invalid_recipe.yaml")
    with open(recipe_path, 'w') as f:
        f.write("invalid yaml: {")  # Invalid YAML content
    with pytest.raises(yaml.YAMLError):
        RecipeExecutor(recipe_path=recipe_path)

def test_recipe_executor_missing_template(temp_dir):
    """Test executing a recipe with a missing template file."""
    recipe_content = """
    name: Test Recipe
    links:
      - name: LLM Link
        type: llm
        template:
          file: nonexistent_template.txt
    """
    recipe_path = os.path.join(temp_dir, "recipe_with_missing_template.yaml")
    with open(recipe_path, 'w') as f:
        f.write(recipe_content)
    executor = RecipeExecutor(recipe_path=recipe_path)
    # The error is raised when execute is called, not when initialized
    with pytest.raises(Exception):
        executor.execute()

def test_recipe_executor_function_raises_exception(temp_dir, monkeypatch):
    """Test executing a recipe with a function that raises an exception."""
    recipe_content = """
    name: Test Recipe
    links:
      - name: Function Link
        type: function
        function:
          name: raising_function
    """
    recipe_path = os.path.join(temp_dir, "recipe_with_raising_function.yaml")
    with open(recipe_path, 'w') as f:
        f.write(recipe_content)
    
    # Mock the function registry to include a function that raises an exception
    def raising_function():
        raise ValueError("Intentional exception")
    
    monkeypatch.setattr("core.executor.FunctionRegistry.get", lambda x: raising_function if x == "raising_function" else None)
    
    executor = RecipeExecutor(recipe_path=recipe_path)
    result = executor.execute()
    assert "error" in result["Function Link"].data
    assert "Intentional exception" in result["Function Link"].data["error"]

def test_recipe_executor_invalid_model_name(temp_dir):
    """Test executing a recipe with an invalid model name."""
    recipe_content = """
    name: Test Recipe
    links:
      - name: LLM Link
        type: llm
        model: invalid-model-name
        prompt: "Say hello"
    """
    recipe_path = os.path.join(temp_dir, "recipe_with_invalid_model.yaml")
    with open(recipe_path, 'w') as f:
        f.write(recipe_content)
    executor = RecipeExecutor(recipe_path=recipe_path)
    result = executor.execute()
    assert "error" in result["LLM Link"].data

def test_recipe_executor_infinite_loop(temp_dir):
    """Test executing a recipe that results in an infinite loop."""
    recipe_content = """
    name: Test Recipe
    links:
      - name: Link1
        type: llm
        prompt: "{{ Link2.data.output }}"
      - name: Link2
        type: llm
        prompt: "{{ Link1.data.output }}"
    """
    recipe_path = os.path.join(temp_dir, "recipe_with_infinite_loop.yaml")
    with open(recipe_path, 'w') as f:
        f.write(recipe_content)
    executor = RecipeExecutor(recipe_path=recipe_path)
    # Now test will detect cycles during execution
    with pytest.raises(Exception, match="Circular dependency"):
        executor.execute()
