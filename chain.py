import logging
import os
import yaml
import json
import re
from typing import Dict, Any, Callable, List, Optional, Union
from pydantic import BaseModel, Field
import jsonschema

# Import LinkConfig from base_link module
from links.base_link import BaseLink, LinkConfig

# Import link implementations
from links.sql_link import SQLLink, SQLLinkConfig
from links.agent_link import AgentLink, AgentLinkConfig
from links.llm_link import LLMLink, LLMLinkConfig
from links.user_input_link import UserInputLink, UserInputLinkConfig

class Chain:
    """
    Main class for creating and executing chains of links.
    Integrates registry functionality and chain execution.
    """
    
    # Registry of all available link handlers
    LINK_REGISTRY = {
        "sql": SQLLink(),
        "agent": AgentLink(),
        "llm": LLMLink(),  # Only use "llm" type
        "user_input": UserInputLink()
    }

    SCHEMA_PATH = os.path.join("schema", "recipe_schema.json")
    
    @classmethod
    def load_schema(cls) -> Dict[str, Any]:
        """
        Load the JSON schema for recipes.
        
        Returns:
            Dict containing the schema definition
        """
        try:
            with open(cls.SCHEMA_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load schema from {cls.SCHEMA_PATH}: {str(e)}")
            raise ValueError(f"Failed to load schema: {str(e)}")

    @classmethod
    def register_link(cls, link_type: str, link_handler: BaseLink) -> None:
        """
        Register a new link handler.
        
        Args:
            link_type: The type identifier for this link
            link_handler: The link instance that handles this link type
        """
        if link_type in cls.LINK_REGISTRY:
            logging.warning(f"Overriding existing link handler for type: {link_type}")
        
        cls.LINK_REGISTRY[link_type] = link_handler
        logging.info(f"Registered link handler for type: {link_type}")
    
    @classmethod
    def get_link_handler(cls, link_type: str) -> BaseLink:
        """
        Get the handler for a specific link type.
        
        Args:
            link_type: The type of link to get a handler for
        
        Returns:
            The link handler
        
        Raises:
            ValueError: If no handler is registered for this link type
        """
        if link_type not in cls.LINK_REGISTRY:
            available_types = list(cls.LINK_REGISTRY.keys())
            raise ValueError(f"No handler registered for link type: {link_type}. Available types: {available_types}")
        
        return cls.LINK_REGISTRY[link_type]
    
    @classmethod
    def get_available_links(cls) -> List[str]:
        """Get list of all registered link types."""
        return list(cls.LINK_REGISTRY.keys())
    
    @classmethod
    def from_recipe_file(cls, filepath: str) -> 'Chain':
        """
        Create a chain from a recipe file.
        
        Args:
            filepath: Path to the recipe YAML file
            
        Returns:
            Chain instance configured with the recipe
        """
        recipe_data = cls.load_recipe_file(filepath)
        return cls(recipe_data)
    
    @staticmethod
    def load_recipe_file(filepath: str) -> Dict[str, Any]:
        """
        Load a recipe from a YAML file.
        
        Args:
            filepath: Path to the YAML file
            
        Returns:
            Parsed recipe data
            
        Raises:
            ValueError: If file not found or contains invalid recipe
        """
        logging.info(f"Loading recipe from file: {filepath}")
        
        try:
            with open(filepath, 'r') as file:
                # Use SafeLoader for security
                recipe_data = yaml.safe_load(file)
                logging.info(f"Successfully loaded recipe file: {filepath}")
                
                # Debug the loaded data structure
                if 'links' in recipe_data:
                    logging.debug(f"Recipe contains {len(recipe_data['links'])} links")
                    
                    for i, link in enumerate(recipe_data['links']):
                        if 'name' in link and 'type' in link:
                            logging.debug(f"Link {i}: name={link['name']}, type={link['type']}")
                
                # Validate structure
                Chain.validate_recipe(recipe_data)
                    
                return recipe_data
                
        except FileNotFoundError:
            logging.error(f"Recipe file not found: {filepath}")
            raise ValueError(f"Recipe file not found: {filepath}")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML in {filepath}: {e}")
            raise ValueError(f"Error parsing YAML in {filepath}: {e}")
        except Exception as e:
            logging.error(f"Error loading recipe {filepath}: {e}")
            raise ValueError(f"Error loading recipe {filepath}: {e}")
    
    @staticmethod
    def validate_recipe(recipe_data: Any) -> bool:
        """
        Validate the structure of a loaded recipe against the schema.
        
        Args:
            recipe_data: Loaded recipe data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # First perform basic structural validation (required since the beginning)
            if not isinstance(recipe_data, dict) or 'links' not in recipe_data:
                logging.error("Recipe must be a dictionary with a 'links' key")
                return False
            
            schema = Chain.load_schema()
            validator = jsonschema.Draft7Validator(schema)
            errors = list(validator.iter_errors(recipe_data))
            
            if errors:
                for error in errors:
                    logging.error(f"Recipe schema validation error: {error}")
                return False
            
            logging.info("Recipe schema validation successful.")
            return True
        except Exception as e:
            logging.error(f"Error during recipe validation: {str(e)}")
            return False

    @classmethod
    def generate_example_recipe(cls) -> Dict[str, Any]:
        """Generate an example recipe that demonstrates all link types."""
        example = {
            "name": "Example Recipe",
            "version": "1.0.0",
            "description": "An example recipe demonstrating all link types",
            "links": [
                {
                    "name": "UserInput",
                    "type": "user_input",
                    "description": "Collect user preferences",
                    "inputs": {
                        "query": {
                            "description": "What would you like to know about?",
                            "required": True
                        },
                        "depth": {
                            "description": "How detailed should the answer be? (1-5)",
                            "type": "number",
                            "default": 3
                        }
                    }
                },
                {
                    "name": "GenerateResponse",
                    "type": "llm",
                    "template": "example_template.txt",
                    "parameters": {
                        "user_query": "{{UserInput_output.data.query}}",
                        "depth": "{{UserInput_output.data.depth}}"
                    },
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "output_format": "json",
                    "output_schema": {
                        "answer": {
                            "type": "str",
                            "description": "The answer to the user's query"
                        },
                        "sources": {
                            "type": "list[str]",
                            "description": "Sources used for this information"
                        }
                    }
                }
            ]
        }
        return example

    def __init__(self, recipe_data: Dict[str, Any]):
        """
        Initialize a chain with recipe data.
        
        Args:
            recipe_data: Recipe configuration dictionary
        """
        self.recipe_data = recipe_data
        # Convert raw link dictionaries to LinkConfig objects
        self.links = [self._create_link_config(link) for link in recipe_data.get('links', [])]
        self.name = recipe_data.get('name', 'unnamed_recipe')
        self.version = recipe_data.get('version', '1.0')
    
    def _create_link_config(self, link_data: Dict[str, Any]) -> LinkConfig:
        """
        Convert a dictionary link configuration to a LinkConfig object.
        
        Args:
            link_data: Dictionary containing link configuration
            
        Returns:
            LinkConfig object
        """
        link_type = link_data.get('type', '')
        if link_type == 'user_input':
            return UserInputLinkConfig(**link_data)
        elif link_type == 'llm':
            return LLMLinkConfig(**link_data)
        elif link_type == 'sql':
            return SQLLinkConfig(**link_data)
        elif link_type == 'agent':
            return AgentLinkConfig(**link_data)
        else:
            return LinkConfig(**link_data)
    
    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the chain with all its linked links.
        
        Args:
            initial_context: Optional initial context to use
            
        Returns:
            Final context after executing all links
        """
        # Initialize context with provided values or empty dict
        context = initial_context or {}
        
        # Debug log context at start (if debug logging enabled)
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            self.log_context(context, "INITIAL CONTEXT")
        
        logging.info(f"Executing chain '{self.name}' (version {self.version}) with {len(self.links)} links")
        
        for i, link_config in enumerate(self.links):
            try:
                # Debug log context before resolving parameters
                logging.debug(f"CONTEXT BEFORE LINK {i+1}: {context}")
                
                # Print this specific link configuration before resolution
                if i == 2:  # Check if it's the third link (index 2)
                    logging.debug(f"LINK 3 CONFIG BEFORE RESOLUTION - name: {link_config.name}, type: {link_config.type}")
                    logging.debug(f"LINK 3 CONFIG BEFORE RESOLUTION - template: {getattr(link_config, 'template', None)}")
                    logging.debug(f"LINK 3 CONFIG BEFORE RESOLUTION - prompt: {getattr(link_config, 'prompt', None)}")
                
                # Resolve parameters in the link configuration
                resolved_link_config = self._resolve_parameters_in_config(link_config, context)
                
                # Print the resolved configuration for the third link
                if i == 2:
                    logging.debug(f"LINK 3 CONFIG AFTER RESOLUTION - name: {resolved_link_config.name}, type: {resolved_link_config.type}")
                    logging.debug(f"LINK 3 CONFIG AFTER RESOLUTION - template: {getattr(resolved_link_config, 'template', None)}")
                    logging.debug(f"LINK 3 CONFIG AFTER RESOLUTION - prompt: {getattr(resolved_link_config, 'prompt', None)}")
                
                # Get link name and type
                link_name = resolved_link_config.name.replace(' ', '_')
                link_type = resolved_link_config.type
                                
                logging.info(f"Processing link {i+1}/{len(self.links)}: {link_name} (Type: {link_type})")
                
                # Get the appropriate link handler and execute the link
                link_handler = self.get_link_handler(link_type)
                # Pass the LinkConfig object directly to the handler
                output = link_handler.execute(resolved_link_config, context)
                
                # Store the output in the context with the link name as key
                output_key = f"{link_name}_output"
                context[output_key] = output
                logging.info(f"Link {link_name} completed, stored result in context as '{output_key}'")
                
                # Validate output against schema if one exists
                if resolved_link_config.output_schema and output.get('success', False):
                    self._validate_output_against_schema(output.get('data', {}), 
                                                       resolved_link_config.output_schema,
                                                       link_name)
                
                # Debug log context after link execution
                logging.debug(f"CONTEXT AFTER LINK {i+1}: {context}")
                    
            except Exception as e:
                logging.error(f"Error processing link {i+1}: {str(e)}")
                # Continue with next link
        
        # Debug log final context
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            self.log_context(context, "FINAL CONTEXT")
        
        # Add chain metadata to results
        context['__chain_metadata__'] = {
            "name": self.name,
            "version": self.version,
            "link_count": len(self.links),
            "completed_links": i + 1
        }
        
        return context
    
    # Add this helper method to recursively resolve placeholders in any object
    def resolve_all_placeholders(self, obj: Any, context: Dict[str, Any]) -> Any:
        import re
        if isinstance(obj, str):
            # Replace each placeholder in the string
            def replacer(match):
                placeholder = match.group(1)
                parts = placeholder.split(".")
                value = context.get(parts[0])
                # If value uses standard output format, use its 'data' field
                if isinstance(value, dict) and "data" in value:
                    value = value["data"]
                for part in parts[1:]:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = match.group(0)
                        break
                if value is None:
                    return ""
                # Convert the value to string and strip wrapping quotes if present
                val_str = str(value)
                if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):
                    val_str = val_str[1:-1]
                return val_str
            return re.sub(r"{{([^{}]+)}}", replacer, obj)
        elif isinstance(obj, list):
            return [self.resolve_all_placeholders(item, context) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.resolve_all_placeholders(v, context) for k, v in obj.items()}
        else:
            return obj

    def _resolve_parameters_in_config(self, config: LinkConfig, context: Dict[str, Any]) -> LinkConfig:
        # Create a copy of the configuration dict to avoid modifying the original (preserve None values)
        config_dict = config.model_dump(exclude_none=False)
        
        # Add detailed logging of the input configuration
        logging.debug(f"CONFIG RESOLUTION - Original config fields: {list(config_dict.keys())}")
        if 'template' in config_dict:
            logging.debug(f"CONFIG RESOLUTION - Original template value: '{config_dict['template']}'")
        if 'prompt' in config_dict:
            logging.debug(f"CONFIG RESOLUTION - Original prompt value: '{config_dict['prompt']}'")
        
        resolved_config = {}
        # Preserve the raw values for "prompt" and "template"
        for key, value in config_dict.items():
            if key in ("prompt", "template"):
                resolved_config[key] = value
                logging.debug(f"CONFIG RESOLUTION - Preserving {key} with value: '{value}'")
            else:
                resolved_config[key] = self.resolve_all_placeholders(value, context)
        
        # Log the final configuration to see what's actually being returned
        logging.debug(f"CONFIG RESOLUTION - Final fields: {list(resolved_config.keys())}")
        if 'template' in resolved_config:
            logging.debug(f"CONFIG RESOLUTION - Final template value: '{resolved_config['template']}'")
        if 'prompt' in resolved_config:
            logging.debug(f"CONFIG RESOLUTION - Final prompt value: '{resolved_config['prompt']}'")
            
        result = config.__class__(**resolved_config)
        
        # Verify template field survived in the final config object
        if hasattr(result, 'template'):
            logging.debug(f"CONFIG RESOLUTION - Returned config has template: '{result.template}'")
        if hasattr(result, 'prompt'):
            logging.debug(f"CONFIG RESOLUTION - Returned config has prompt: '{result.prompt}'")
        
        return result

    def _validate_output_against_schema(self, output_data: Any, schema: Dict[str, Any], link_name: str) -> bool:
        """
        Validate the output data against the provided schema.
        
        Args:
            output_data: The data to validate
            schema: The schema to validate against
            link_name: Name of the link (for logging)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Convert schema to JSON Schema format if it's not already
            json_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for field_name, field_def in schema.items():
                if isinstance(field_def, dict):
                    field_type = field_def.get('type', 'string')
                    json_schema['properties'][field_name] = {"type": field_type}
                    
                    # Add to required fields if specified
                    if field_def.get('required', False):
                        json_schema['required'].append(field_name)
            
            # Validate
            jsonschema.validate(output_data, json_schema)
            logging.debug(f"Output from link '{link_name}' successfully validated against schema")
            return True
        except jsonschema.exceptions.ValidationError as e:
            logging.warning(f"Output from link '{link_name}' failed schema validation: {e}")
            return False
        except Exception as e:
            logging.error(f"Error during output validation: {str(e)}")
            return False
    
    def resolve_parameters(self, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameters in the link configuration by replacing placeholders with values from context.
        
        Args:
            link_config: The configuration for the link
            context: The current context of the recipe execution containing outputs from previous links
            
        Returns:
            Updated link configuration with resolved parameters
        """
        # Get link name for logging
        link_name = link_config.get('name', 'unnamed_link')
        logging.debug(f"PARAMETER RESOLVER - Resolving for link: {link_name}")
        
        # If the link has no parameters, return it as is
        if "parameters" not in link_config:
            logging.debug("No parameters to resolve in this link")
            return link_config
            
        # Make a deep copy to avoid modifying the original
        resolved_config = link_config.copy()
        resolved_params = {}
        
        # Resolve each parameter
        for param_name, param_value in link_config["parameters"].items():
            # Skip null values
            if param_value is None:
                resolved_params[param_name] = None
                continue
                
            if isinstance(param_value, str):
                # Check if this parameter is a reference to a previous link output
                match = re.match(r"{{([^.}]+)(?:\.([^}]+))?}}", param_value)
                
                if match:
                    logging.debug(f"Found placeholder in parameter '{param_name}': {param_value}")
                    source_name = match.group(1)
                    logging.debug(f"Source name: {source_name}")
                    field_path = match.group(2)
                    logging.debug(f"Field path: {field_path}")
                    
                    # Source is either a link output or direct command-line argument
                    if source_name.endswith("_output") and source_name in context:
                        logging.debug(f"Found output reference in context: {source_name}")
                        source_value = context[source_name]
                        logging.debug(f"Source value: {source_value}")

                        # Check if output follows standard format with data field
                        if isinstance(source_value, dict) and "data" in source_value:
                            source_value = source_value["data"]
                            logging.debug(f"Extracted 'data' field from output: {source_value}")
                        
                        # Navigate to the field if specified
                        if field_path:
                            logging.debug(f"Resolving field path: {field_path}")
                            try:
                                # Handle case where output is a JSON string
                                if isinstance(source_value, str):
                                    logging.debug(f"Source value is a string: {source_value}")
                                    if source_value.startswith('{') or source_value.startswith('['):
                                        try:
                                            logging.debug("Attempting to parse JSON string")
                                            source_value = json.loads(source_value)
                                        except json.JSONDecodeError:
                                            logging.warning(f"Failed to parse JSON: {source_value}")
                                    elif source_value.startswith('```json') and source_value.endswith('```'):
                                        # Handle markdown-formatted JSON output
                                        try:
                                            logging.debug("Attempting to parse markdown JSON")
                                            json_str = source_value.replace('```json', '').replace('```', '').strip()
                                            source_value = json.loads(json_str)
                                            logging.debug(f"Parsed JSON: {source_value}")
                                        except json.JSONDecodeError:
                                            logging.warning(f"Failed to parse markdown JSON: {source_value}")
                                
                                # Extract nested field
                                for field in field_path.split('.'):
                                    logging.debug(f"Accessing field: {field}")
                                    if isinstance(source_value, dict) and field in source_value:
                                        logging.debug(f"Field found in dict: {source_value[field]}")
                                        source_value = source_value[field]
                                    elif hasattr(source_value, field):
                                        logging.debug(f"Field found in object: {getattr(source_value, field)}")
                                        source_value = getattr(source_value, field)
                                    else:
                                        # Field not found - use a safe fallback value
                                        logging.warning(f"Field {field} not found in {source_name}, using fallback value")
                                        source_value = f"MISSING_FIELD_{field}"
                                        break
                                    
                                resolved_params[param_name] = source_value
                            except (KeyError, TypeError, AttributeError) as e:
                                logging.error(f"Failed to access field {field_path} in {source_value}: {e}")
                                # Use a fallback value instead of error message
                                resolved_params[param_name] = f"MISSING_FIELD_{field_path}"
                        else:
                            # Use the entire output
                            logging.debug(f"No field path specified, using full output: {source_value}")
                            resolved_params[param_name] = source_value
                    else:
                        # It's a direct reference to a command-line or environment parameter
                        logging.debug(f"Direct reference not found in context: {source_name}")
                        resolved_params[param_name] = param_value
                else:
                    # Not a placeholder, use as is
                    logging.debug(f"No placeholder found in parameter '{param_name}', using as is")
                    resolved_params[param_name] = param_value
            else:
                # Not a string (e.g., a number or boolean), use as is
                logging.debug(f"Parameter '{param_name}' is not a string, using as is")
                resolved_params[param_name] = param_value
        
        resolved_config["parameters"] = resolved_params
        logging.debug(f"Resolved parameters for link '{link_name}': {resolved_params}")
        return resolved_config
    
    def log_context(self, context: Dict[str, Any], label: str = "DEBUG CONTEXT") -> Dict[str, Any]:
        """
        Log the current execution context for debugging purposes.
        
        Args:
            context: The context to debug
            label: Optional label for the log output
            
        Returns:
            A summary of the context
        """
        if not context:
            logging.debug("Empty context provided to log_context")
            return {"context_keys": [], "content_summary": {}}
            
        logging.debug(f"=== {label} ===")
        logging.debug(f"Available context keys: {list(context.keys())}")
        
        # Print details about each context item
        for key, value in context.items():
            if isinstance(value, dict):
                # For dict values, show keys and structure
                if "data" in value and "success" in value:
                    # Standard output format
                    success = value.get("success", False)
                    status = "✅" if success else "❌"
                    data_keys = list(value.get("data", {}).keys())
                    error = value.get("error", "None")
                    logging.debug(f"{status} {key}: data_keys={data_keys}, error={error}")
                else:
                    # Regular dict
                    logging.debug(f"📄 {key}: dict with keys={list(value.keys())}")
            else:
                # For non-dict values, show type and preview
                try:
                    preview = str(value)[:50] + ("..." if len(str(value)) > 50 else "")
                    logging.debug(f"🔹 {key}: ({type(value).__name__}) {preview}")
                except:
                    logging.debug(f"🔹 {key}: (unable to display)")
        
        logging.debug("==================")
        
        return {
            "context_keys": list(context.keys()),
            "content_summary": {k: type(v).__name__ for k, v in context.items()}
        }
