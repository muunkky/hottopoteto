import os
import yaml
import json
import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import jsonschema

# Import LinkConfig from base_link module
from links.base_link import BaseLink, LinkConfig

# Import link implementations
from links.sql_link import SQLLink, SQLLinkConfig
from links.agent_link import AgentLink, AgentLinkConfig
from links.llm_link import LLMLink, LLMLinkConfig
from links.user_input_link import UserInputLink, UserInputLinkConfig

logger = logging.getLogger(__name__)

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
            raise ValueError(f"Failed to load schema: {str(e)}")

    @classmethod
    def register_link(cls, link_type: str, link_handler: BaseLink) -> None:
        """
        Register a new link handler.
        
        Args:
            link_type: The type identifier for this link
            link_handler: The link instance that handles this link type
        """
        cls.LINK_REGISTRY[link_type] = link_handler
    
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
        logging.info(f"Loading recipe file: {filepath}")
        recipe_data = cls.load_recipe_file(filepath)
        chain = cls(recipe_data)
        logging.debug("Chain instance created from recipe file.")
        return chain
    
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
        try:
            with open(filepath, 'r') as file:
                recipe_data = yaml.safe_load(file)
            
            if not Chain.validate_recipe(recipe_data):
                raise ValueError("Recipe validation failed")
            
            return recipe_data
                
        except FileNotFoundError:
            raise ValueError(f"Recipe file not found: {filepath}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML in {filepath}: {e}")
        except Exception as e:
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
            if not isinstance(recipe_data, dict) or 'links' not in recipe_data:
                return False
            
            schema = Chain.load_schema()
            validator = jsonschema.Draft7Validator(schema)
            errors = list(validator.iter_errors(recipe_data))
            
            if errors:
                return False
            
            return True
        except Exception as e:
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
            config_obj = UserInputLinkConfig(**link_data)
        elif link_type == 'llm':
            config_obj = LLMLinkConfig(**link_data)
        elif link_type == 'sql':
            config_obj = SQLLinkConfig(**link_data)
        elif link_type == 'agent':
            config_obj = AgentLinkConfig(**link_data)
        else:
            config_obj = LinkConfig(**link_data)
        return config_obj
    
    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the chain with all its linked links.
        
        Args:
            initial_context: Optional initial context to use
            
        Returns:
            Final context after executing all links
        """
        logging.info("Starting chain execution.")
        context = initial_context or {}
        
        for i, link_config in enumerate(self.links):
            try:
                resolved_link_config = self._resolve_parameters_in_config(link_config, context)
                link_name = resolved_link_config.name.replace(' ', '_')
                link_type = resolved_link_config.type
                link_handler = self.get_link_handler(link_type)
                output = link_handler.execute(resolved_link_config, context)
                output_key = f"{link_name}_output"
                context[output_key] = output
                
                if resolved_link_config.output_schema and output.get('success', False):
                    self._validate_output_against_schema(output.get('data', {}), 
                                                       resolved_link_config.output_schema,
                                                       link_name)
                    
            except Exception as e:
                pass
        
        context['__chain_metadata__'] = {
            "name": self.name,
            "version": self.version,
            "link_count": len(self.links),
            "completed_links": i + 1
        }
        
        logging.info("Chain execution finished.")
        return context
    
    def resolve_all_placeholders(self, obj: Any, context: Dict[str, Any]) -> Any:
        import re
        if isinstance(obj, str):
            def replacer(match):
                placeholder = match.group(1)
                parts = placeholder.split(".")
                value = context.get(parts[0])
                
                for part in parts[1:]:
                    if value is None:
                        break
                    elif isinstance(value, dict) and part in value:
                        value = value[part]
                    elif hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        value = None
                        break
                        
                if value is None:
                    return ""
                    
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
        config_dict = config.model_dump(exclude_none=False)
        resolved_config = {}
        for key, value in config_dict.items():
            resolved_config[key] = self.resolve_all_placeholders(value, context)
        result = config.__class__(**resolved_config)
        return result

    def _validate_output_against_schema(self, output_data: Any, schema: Dict[str, Any], link_name: str) -> bool:
        try:
            json_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for field_name, field_def in schema.items():
                if isinstance(field_def, dict):
                    field_type = field_def.get('type', 'string')
                    json_schema['properties'][field_name] = {"type": field_type}
                    
                    if field_def.get('required', False):
                        json_schema['required'].append(field_name)
            
            jsonschema.validate(output_data, json_schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            return False
        except Exception as e:
            return False
    
    def resolve_parameters(self, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        link_name = link_config.get('name', 'unnamed_link')
        
        if "parameters" not in link_config:
            return link_config
            
        resolved_config = link_config.copy()
        resolved_params = {}
        
        for param_name, param_value in link_config["parameters"].items():
            if param_value is None:
                resolved_params[param_name] = None
                continue
                
            if isinstance(param_value, str):
                match = re.match(r"{{([^.}]+)(?:\.([^}]+))?}}", param_value)
                
                if match:
                    source_name = match.group(1)
                    field_path = match.group(2)
                    
                    if source_name.endswith("_output") and source_name in context:
                        source_value = context[source_name]

                        if isinstance(source_value, dict) and "data" in source_value:
                            source_value = source_value["data"]
                        
                        if field_path:
                            try:
                                if isinstance(source_value, str):
                                    if source_value.startswith('{') or source_value.startswith('['):
                                        try:
                                            source_value = json.loads(source_value)
                                        except json.JSONDecodeError:
                                            pass
                                    elif source_value.startswith('```json') and source_value.endswith('```'):
                                        try:
                                            json_str = source_value.replace('```json', '').replace('```', '').strip()
                                            source_value = json.loads(json_str)
                                        except json.JSONDecodeError:
                                            pass
                                
                                for field in field_path.split('.'):
                                    if isinstance(source_value, dict) and field in source_value:
                                        source_value = source_value[field]
                                    elif hasattr(source_value, field):
                                        source_value = getattr(source_value, field)
                                    else:
                                        source_value = f"MISSING_FIELD_{field}"
                                        break
                                    
                                resolved_params[param_name] = source_value
                            except (KeyError, TypeError, AttributeError) as e:
                                resolved_params[param_name] = f"MISSING_FIELD_{field_path}"
                        else:
                            resolved_params[param_name] = source_value
                    else:
                        resolved_params[param_name] = param_value
                else:
                    resolved_params[param_name] = param_value
            else:
                resolved_params[param_name] = param_value
        
        resolved_config["parameters"] = resolved_params
        return resolved_config
    
    def log_context(self, context: Dict[str, Any], label: str = "DEBUG CONTEXT") -> Dict[str, Any]:
        if not context:
            return {"context_keys": [], "content_summary": {}}
            
        return {
            "context_keys": list(context.keys()),
            "content_summary": {k: type(v).__name__ for k, v in context.items()}
        }
