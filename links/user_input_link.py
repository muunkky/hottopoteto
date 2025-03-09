import json
import logging
import sys
from typing import Dict, Any, Optional, List, ClassVar
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from links.base_link import BaseLink, LinkConfig  # Import LinkConfig from base_link

# Constants for default values
DEFAULT_INPUT_TYPE = "string"
DEFAULT_FALLBACK_VALUES = {
    "user_input": "vanilla ice cream with chocolate chips",
    "dietary_restrictions": "none",
    "target_audience": "general consumers",
    "complexity_level": 3
}

class UserInputLinkConfig(LinkConfig):
    """Extended configuration for user input with specific fields"""
    # Default constants that can be easily modified
    DEFAULT_TYPE: ClassVar[str] = "user_input"
    
    # Fields for user input configuration
    inputs: Optional[Dict[str, Dict[str, Any]]] = None
    default_values: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Template-based input fields
    template: Optional[str] = None
    template_file: Optional[str] = None
    
    # Auto-set type if not provided
    @field_validator('type', mode='before')
    @classmethod
    def set_default_type(cls, v):
        return v or cls.DEFAULT_TYPE

class UserInputLink(BaseLink):
    """Link for executing user input links."""
    
    # Class constants for configuration
    DEFAULT_INPUT_TYPE = DEFAULT_INPUT_TYPE
    DEFAULT_FALLBACK_VALUES = DEFAULT_FALLBACK_VALUES
    
    def get_required_fields(self) -> list:
        """Returns list of required fields for user input links."""
        return ["name", "type"]
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        """
        Validate user input configuration.
        
        Args:
            config: The LinkConfig object to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Either inputs field or template/template_file should exist
        inputs = None
        template = None
        template_file = None

        # Handle both standard LinkConfig and specialized UserInputLinkConfig
        if isinstance(config, UserInputLinkConfig):
            logging.debug("Config is UserInputLinkConfig")
            inputs = config.inputs
            template = config.template
            template_file = config.template_file
        else:
            logging.debug("Trying to extract from parameters or top-level fields of LinkConfig")
            config_dict = config.dict()
            inputs = config_dict.get("inputs")
            template = config_dict.get("template")
            template_file = config_dict.get("template_file")

        logging.debug(f"Validating UserInputLink config: {config}")

        if not inputs and not template and not template_file:
            logging.warning(f"No input fields or template defined for {config.name}")

        # If template_file is provided, validate it exists
        if template_file:
            try:
                self._validate_file_path(template_file)
            except ValueError as e:
                raise ValueError(f"Template file validation error: {str(e)}")
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementation of user input collection.
        
        Args:
            config: The LinkConfig object for this link
            context: Current execution context
            
        Returns:
            The collected user inputs
        """
        link_name = config.name
        logging.info(f"👤 Starting user input link: {link_name}")
        
        # Use model_dump/dict with exclude_none=False to preserve subclass fields like "inputs"
        link_config = config.dict(exclude_none=False)
        logging.debug(f"UserInputLink config: {link_config}")
        
        # Try to load template if specified
        template_content = None
        if "template_file" in link_config:
            template_file = link_config["template_file"]
        
            logging.debug(f"Executing UserInputLink link_config: {link_config}")
        
        elif "template" in link_config:
            template_content = link_config["template"]
            logging.debug(f"Using inline template ({len(template_content)} chars)")
            
        # If template exists, format it with context variables
        if template_content:
            logging.debug("Resolving parameters for template")
            resolved_params = self.resolve_context_references(link_config, context)
            try:
                logging.debug("Formatting template with parameters")
                formatted_template = self.format_template_with_params(template_content, resolved_params)
                print("\n" + formatted_template + "\n")
            except ValueError as e:
                logging.warning(f"⚠️ Error formatting template: {str(e)}")
                # Continue with default template
        
        # Extract inputs field
        inputs = None
        if "inputs" in link_config:
            inputs = link_config["inputs"]
            logging.debug(f"Found {len(inputs)} inputs in 'inputs' field")
        
        # Display input header
        print("\n" + "="*50)
        print(f"  {config.description or 'User Input'}")
        print("="*50)
        
        # Output schema will be used to shape our result
        output_schema = config.output_schema or {}
        
        # Create result dictionary for collected inputs
        result = {}
        
        # Generate inputs from schema if needed
        if not inputs and output_schema:
            logging.info("No inputs defined, creating from output schema")
            inputs = {}
            for field, details in output_schema.items():
                inputs[field] = {
                    "description": details.get("description", f"Enter value for {field}"),
                    "required": True  # Make schema fields required by default
                }
            logging.debug(f"Created {len(inputs)} inputs from output schema: {list(inputs.keys())}")
        
        # If still no inputs defined, use default values
        if not inputs:
            logging.warning("⚠️ No input fields defined in link configuration")
            
            # Use default values, prioritizing config over class defaults
            # First check for default_values in the specialized config
            if isinstance(config, UserInputLinkConfig) and config.default_values:
                result = config.default_values.copy()
                logging.info(f"Using specialized config default values: {result}")
            # Then check for default_values in the link config
            elif "default_values" in link_config:
                result = link_config["default_values"].copy()
                logging.info(f"Using link config default values: {result}")
            # Finally fall back to class constants
            else:
                result = self.DEFAULT_FALLBACK_VALUES.copy()
                logging.info(f"Using class default values: {result}")
            
            return {"inputs": result}
        
        # Process each input field
        logging.info(f"Collecting {len(inputs)} inputs from user")
        for input_name, input_config in inputs.items():
            # Extract configuration
            description = input_config.get("description", input_name)
            required = input_config.get("required", False)
            default = input_config.get("default", "")
            input_type = input_config.get("type", self.DEFAULT_INPUT_TYPE)
            
            logging.debug(f"Collecting input '{input_name}' (required={required}, type={input_type})")
            
            # Build prompt
            prompt = f"{description}"
            if default:
                prompt += f" [default: {default}]"
            prompt += ": "
            
            # Use a separate line for cleaner appearance
            print("\n>>> " + prompt, end="", flush=True)
            
            # Keep trying until we get valid input
            valid_input = False
            while not valid_input:
                try:
                    # Read user input
                    user_input = input()
                    logging.debug(f"Raw input for '{input_name}': '{user_input}'")
                    
                    # Use default if input is empty
                    if not user_input and default:
                        user_input = default
                        print(f"Using default: {default}")
                        logging.debug(f"Using default value: {default}")
                    
                    # Validate input
                    if required and not user_input:
                        print("This input is required. Please provide a value: ", end="", flush=True)
                        logging.debug("Empty input rejected - field is required")
                        continue
                    
                    # Type conversion for numbers
                    if input_type == "number":
                        try:
                            user_input = float(user_input)
                            logging.debug(f"Converted input to number: {user_input}")
                            
                            # Check min/max constraints
                            min_val = input_config.get("min")
                            max_val = input_config.get("max")
                            
                            if min_val is not None and user_input < min_val:
                                print(f"Value must be at least {min_val}: ", end="", flush=True)
                                logging.debug(f"Input {user_input} below minimum {min_val}")
                                continue
                                
                            if max_val is not None and user_input > max_val:
                                print(f"Value must be at most {max_val}: ", end="", flush=True)
                                logging.debug(f"Input {user_input} above maximum {max_val}")
                                continue
                                
                        except ValueError:
                            print("Please enter a valid number: ", end="", flush=True)
                            logging.debug(f"Failed to convert '{user_input}' to number")
                            continue
                    
                    # If we get here, input is valid
                    result[input_name] = user_input
                    logging.debug(f"Accepted value for '{input_name}': {user_input}")
                    valid_input = True
                    
                except Exception as e:
                    logging.error(f"❌ Error while collecting input: {str(e)}")
                    print(f"An error occurred: {str(e)}. Please try again: ", end="", flush=True)
        
        # Show collected inputs
        print("\nCollected inputs:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        logging.info(f"✅ User input collection completed with {len(result)} fields")
        logging.debug(f"Collected inputs: {result}")
        
        return {"inputs": result}
