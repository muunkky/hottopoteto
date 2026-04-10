"""
Shared pytest fixtures and configuration for hottopoteto tests.

Provides reusable test fixtures for recipes, domains, plugins, and RecipeExecutor.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_output_dir():
    """
    Provides a temporary output directory for test execution.
    Automatically cleaned up after test completion.
    """
    temp_dir = tempfile.mkdtemp(prefix="hottopoteto_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_recipe_yaml() -> Dict[str, Any]:
    """Provides a sample recipe structure for testing."""
    return {
        "name": "Test Recipe",
        "description": "A simple test recipe",
        "version": "1.0",
        "domain": "generic",
        "links": [
            {
                "name": "TestLink",
                "type": "llm",
                "provider": "openai",
                "model": "gpt-4o",
                "prompt": "Test prompt",
                "temperature": 0.7,
            }
        ],
    }


@pytest.fixture
def sample_recipe_file(tmp_path, sample_recipe_yaml):
    """
    Creates a temporary recipe YAML file for testing.
    Returns the path to the created file.
    """
    import yaml

    recipe_file = tmp_path / "test_recipe.yaml"
    with open(recipe_file, "w") as f:
        yaml.dump(sample_recipe_yaml, f)
    return recipe_file


@pytest.fixture
def mock_executor_context():
    """Provides a mock context for RecipeExecutor testing."""
    return {
        "variables": {},
        "conversation_history": {},
        "output_dir": "output/test",
        "recipe_name": "test_recipe",
    }


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom marks."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "architecture: mark test as an architecture test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their directory."""
    for item in items:
        rel_path = Path(item.fspath).relative_to(Path(__file__).parent)
        if "unit" in rel_path.parts:
            item.add_marker(pytest.mark.unit)
        elif "integration" in rel_path.parts:
            item.add_marker(pytest.mark.integration)
        elif "architecture" in rel_path.parts:
            item.add_marker(pytest.mark.architecture)
