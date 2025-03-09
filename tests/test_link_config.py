import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
import logging
from typing import Dict, Any, Optional, List, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from links.base_link import LinkConfig, BaseLink
from chain import Chain

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)

class TestLinkConfig(unittest.TestCase):
    """Test cases for LinkConfig and related functionality."""
    
    def test_link_config_creation(self):
        """Test creating a LinkConfig with basic properties."""
        config = LinkConfig(
            name="test_step",
            type="test_type",
            description="Test step",
            parameters={"param1": "value1", "param2": 42}
        )
        
        self.assertEqual(config.name, "test_step")
        self.assertEqual(config.type, "test_type")
        self.assertEqual(config.description, "Test step")
        self.assertEqual(config.parameters["param1"], "value1")
        self.assertEqual(config.parameters["param2"], 42)
        
    def test_link_config_serialization(self):
        """Test serializing a LinkConfig to a dictionary."""
        config = LinkConfig(
            name="test_step",
            type="test_type",
            description="Test step",
            parameters={"param1": "value1", "param2": 42},
            output_format="json",
            output_schema={"field1": {"type": "string"}}
        )
        
        config_dict = config.model_dump()
        
        self.assertEqual(config_dict["name"], "test_step")
        self.assertEqual(config_dict["type"], "test_type")
        self.assertEqual(config_dict["description"], "Test step")
        self.assertEqual(config_dict["parameters"]["param1"], "value1")
        self.assertEqual(config_dict["output_format"], "json")
        self.assertEqual(config_dict["output_schema"]["field1"]["type"], "string")
    
    def test_link_config_validation(self):
        """Test validation of required fields in LinkConfig."""
        # Name is required
        with self.assertRaises(Exception):
            LinkConfig(type="test_type")
        
        # Type is required
        with self.assertRaises(Exception):
            LinkConfig(name="test_step")
        
        # But description and parameters are optional
        config = LinkConfig(name="test_step", type="test_type")
        self.assertEqual(config.name, "test_step")
        self.assertEqual(config.type, "test_type")
        self.assertEqual(config.description, None)
        self.assertEqual(config.parameters, {})
    
    def test_basic_link_validation(self):
        """Test BaseLink's validation of LinkConfig."""
        class TestLink(BaseLink):
            def get_required_fields(self) -> list:
                return ["name", "type", "custom_field"]
                
            def _validate_config_impl(self, config: LinkConfig) -> None:
                if "custom_field" not in config.parameters:
                    raise ValueError("Missing custom_field parameter")
                    
            def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
                return {"result": config.parameters.get("custom_field")}
        
        test_link = TestLink()
        
        # Valid config
        valid_config = LinkConfig(
            name="test_step",
            type="test_type",
            parameters={"custom_field": "test_value"}
        )
        
        test_link.validate_config(valid_config)
        
        # Invalid config - missing custom_field
        invalid_config = LinkConfig(
            name="test_step",
            type="test_type"
        )
        
        with self.assertRaises(ValueError):
            test_link.validate_config(invalid_config)
    
    def test_link_config_in_chain(self):
        """Test that Chain can properly use LinkConfig objects."""
        # Mock chain and registry
        with patch('chain.Chain.LINK_REGISTRY', {"mock": MagicMock()}):
            with patch('chain.Chain._resolve_parameters_in_config') as mock_resolve:
                # Set up the mock to return the config unchanged
                mock_resolve.side_effect = lambda config, context: config
                
                # Create a chain with a mock step
                chain = Chain({
                    "name": "test_chain",
                    "steps": [
                        {
                            "name": "mock_step",
                            "type": "mock",
                            "parameters": {"param1": "value1"}
                        }
                    ]
                })
                
                # Verify that steps are converted to LinkConfig objects
                self.assertEqual(len(chain.steps), 1)
                self.assertIsInstance(chain.steps[0], LinkConfig)
                self.assertEqual(chain.steps[0].name, "mock_step")
                self.assertEqual(chain.steps[0].type, "mock")

class MockLink(BaseLink):
    """Mock implementation of BaseLink for testing."""
    
    def get_required_fields(self) -> list:
        return ["name", "type"]
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        # Simple mock implementation
        return {"mock_result": "success"}

if __name__ == '__main__':
    unittest.main()
