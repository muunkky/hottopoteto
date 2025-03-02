# tests/test_config_loader.py

import os
import tempfile
import unittest
from utils.config_loader import load_config
from models import Recipe

class TestConfigLoader(unittest.TestCase):

    def test_load_config_valid(self):
        """
        Test that a valid YAML configuration loads correctly and environment
        variable placeholders are substituted.
        """
        valid_yaml = """
steps:
  - name: "Test Prompt"
    type: "prompt"
    template: "${TEMPLATE_PATH}"
    parameters:
      user_input: "hello"
    output_format: "text"
    token_limit: 150
"""
        # Set an environment variable for substitution.
        os.environ["TEMPLATE_PATH"] = "prompts/test_prompt.txt"
        
        # Create a temporary file with the valid YAML content.
        with tempfile.NamedTemporaryFile("w+", delete=False) as temp_file:
            temp_file.write(valid_yaml)
            temp_file.flush()
            temp_filepath = temp_file.name
        
        try:
            # Load configuration using our loader.
            recipe = load_config(temp_filepath)
        finally:
            # Clean up the temporary file.
            os.remove(temp_filepath)
        
        # Validate the loaded configuration.
        self.assertEqual(len(recipe.steps), 1)
        step = recipe.steps[0]
        self.assertEqual(step.name, "Test Prompt")
        self.assertEqual(step.type, "prompt")
        self.assertEqual(step.template, "prompts/test_prompt.txt")  # Check substitution.
        self.assertEqual(step.parameters["user_input"], "hello")
        self.assertEqual(step.output_format, "text")
        self.assertEqual(step.token_limit, 150)

    def test_load_config_missing_file(self):
        """
        Test that attempting to load a non-existent file raises FileNotFoundError.
        """
        with self.assertRaises(FileNotFoundError):
            load_config("non_existent_file.yaml")

    def test_load_config_invalid_yaml(self):
        """
        Test that an invalid YAML file triggers a YAML parsing error.
        """
        invalid_yaml = "steps: [this is not valid YAML: because it's missing quotes"
        with tempfile.NamedTemporaryFile("w+", delete=False) as temp_file:
            temp_file.write(invalid_yaml)
            temp_file.flush()
            temp_filepath = temp_file.name
        
        try:
            with self.assertRaises(Exception):
                load_config(temp_filepath)
        finally:
            os.remove(temp_filepath)

    def test_load_config_invalid_schema(self):
        """
        Test that a YAML file with valid YAML syntax but an invalid schema (missing
        required fields) raises a validation error.
        """
        invalid_schema_yaml = """
steps:
  - name: "Invalid Step"
    type: "prompt"
    # Missing required field: output_format
    template: "prompts/invalid_prompt.txt"
"""
        with tempfile.NamedTemporaryFile("w+", delete=False) as temp_file:
            temp_file.write(invalid_schema_yaml)
            temp_file.flush()
            temp_filepath = temp_file.name
        
        try:
            with self.assertRaises(ValueError):
                load_config(temp_filepath)
        finally:
            os.remove(temp_filepath)

if __name__ == '__main__':
    unittest.main()
