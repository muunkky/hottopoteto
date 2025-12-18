"""
Shared pytest fixtures and configuration for hottopoteto tests.

This conftest.py provides reusable test fixtures for recipes, domains,
plugins, and the RecipeExecutor.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_output_dir():
    """
    Provides a temporary output directory for test execution.
    
    Automatically cleaned up after test completion.
    
    Yields:
        Path: Temporary directory path
    """
    temp_dir = tempfile.mkdtemp(prefix="hottopoteto_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_recipe_yaml() -> Dict[str, Any]:
    """
    Provides a sample recipe structure for testing.
    
    Returns:
        Dict[str, Any]: Recipe configuration dictionary
    """
    return {
        "name": "Test Recipe",
        "description": "A simple test recipe",
        "version": "1.0",
        "domain": "llm",
        "links": [
            {
                "name": "TestLink",
                "type": "llm",
                "provider": "openai",
                "model": "gpt-4o",
                "prompt": "Test prompt",
                "temperature": 0.7
            }
        ]
    }


@pytest.fixture
def sample_recipe_file(tmp_path, sample_recipe_yaml):
    """
    Creates a temporary recipe YAML file for testing.
    
    Args:
        tmp_path: pytest built-in tmp_path fixture
        sample_recipe_yaml: Sample recipe data fixture
        
    Returns:
        Path: Path to created recipe file
    """
    import yaml
    
    recipe_file = tmp_path / "test_recipe.yaml"
    with open(recipe_file, 'w') as f:
        yaml.dump(sample_recipe_yaml, f)
    
    return recipe_file


@pytest.fixture
def mock_domain():
    """
    Provides a mock domain for testing domain registration.
    
    Returns:
        Dict[str, Any]: Mock domain configuration
    """
    return {
        "name": "test_domain",
        "description": "Test domain for unit testing",
        "version": "1.0",
        "capabilities": ["test_capability"]
    }


@pytest.fixture
def mock_executor_context():
    """
    Provides a mock context for RecipeExecutor testing.
    
    Returns:
        Dict[str, Any]: Mock execution context
    """
    return {
        "variables": {},
        "conversation_history": {},
        "output_dir": "output/test",
        "recipe_name": "test_recipe"
    }


@pytest.fixture(autouse=True)
def reset_domain_registry():
    """
    Automatically resets the package registry before each test.
    
    This prevents test pollution from package/domain registrations.
    """
    from core.registry import PackageRegistry
    
    # Store original state
    original_packages = PackageRegistry._packages.copy() if hasattr(PackageRegistry, '_packages') else {}
    original_domains = PackageRegistry._domains.copy() if hasattr(PackageRegistry, '_domains') else {}
    
    yield
    
    # Restore original state after test
    if hasattr(PackageRegistry, '_packages'):
        PackageRegistry._packages = original_packages
    if hasattr(PackageRegistry, '_domains'):
        PackageRegistry._domains = original_domains


@pytest.fixture
def sample_llm_recipe_path():
    """
    Provides path to actual example LLM recipe from templates.
    
    Returns:
        Path: Path to llm_example.yaml
    """
    return Path(__file__).parent.parent / "templates" / "recipes" / "examples" / "llm_example.yaml"


@pytest.fixture
def sample_mongodb_recipe_path():
    """
    Provides path to actual example MongoDB recipe from templates.
    
    Returns:
        Path: Path to mongodb_example.yaml
    """
    return Path(__file__).parent.parent / "templates" / "recipes" / "examples" / "mongodb_example.yaml"


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically mark tests based on their location.
    
    - tests/unit/* are marked as @pytest.mark.unit
    - tests/integration/* are marked as @pytest.mark.integration
    """
    for item in items:
        # Get relative path from tests directory
        rel_path = Path(item.fspath).relative_to(Path(__file__).parent)
        
        if "unit" in rel_path.parts:
            item.add_marker(pytest.mark.unit)
        elif "integration" in rel_path.parts:
            item.add_marker(pytest.mark.integration)
