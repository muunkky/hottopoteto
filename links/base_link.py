import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, ClassVar
from pydantic import BaseModel, Field, ValidationError

# Default prompt directory - can be overridden by config
DEFAULT_PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

logger = logging.getLogger(__name__)
class LinkConfig(BaseModel):
    """Base model for step configuration."""
    name: str
    type: str
    description: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    conversation: str = "default"  # added conversation field with default "default"
    
    # Class variable for required fields - subclasses can extend this
    required_fields: ClassVar[List[str]] = ["name", "type"]
    
    @classmethod
    def get_required_fields(cls) -> List[str]:
        """Get the list of required fields for this config."""
        return cls.required_fields
    
    def get_schema(self) -> Dict[str, Any]:
        # Return the JSON schema for this config
        return self.schema()

class OutputData(BaseModel):
    raw: Any = Field(default=None, description="Raw, unprocessed output")
    json: Optional[Dict[str, Any]] = Field(default=None, description="Schema-driven JSON formatted output")

class LinkOutput(BaseModel):
    """Standardized output format for all links."""
    success: bool = True
    data: OutputData = Field(default_factory=OutputData, description="Container for raw and JSON output")
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseLink:
    """Base class for all link implementations."""
    
    # Add class attribute for prompt directory
    prompt_directory = DEFAULT_PROMPT_DIR
    
    @classmethod
    def set_prompt_directory(cls, directory_path: str) -> None:
        """
        Set the base directory for prompt template files.
        
        Args:
            directory_path: Path to the prompt templates directory
        """
        logging.info(f"Setting prompt directory to: {directory_path}")
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        
        cls.prompt_directory = directory_path
    
    @classmethod
    def get_prompt_path(cls, prompt_name: str) -> str:
        """
        Get the full path for a prompt template file.
        
        Args:
            prompt_name: Relative path or name of the prompt file
            
        Returns:
            Full path to the prompt file
        """
        # If it's already an absolute path, return as is
        if os.path.isabs(prompt_name):
            return prompt_name
            
        # If it already contains the prompt directory, return as is
        if (prompt_name.startswith(cls.prompt_directory)):
            return prompt_name
            
        # Otherwise, join with the prompt directory
        return os.path.join(cls.prompt_directory, prompt_name)
    
    def validate_config(self, config: LinkConfig) -> None:
        """
        Validates that the LinkConfig contains all required fields for this link type.
        
        Args:
            config: The LinkConfig object to validate
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = config.get_required_fields()
        
        # Check that required fields exist in the config object
        for field in required_fields:
            if not hasattr(config, field) or getattr(config, field) is None:
                # Special case for parameters that might be in the config.parameters dict
                if field not in ['name', 'type'] and hasattr(config, 'parameters') and config.parameters and field in config.parameters:
                    continue
                
                raise ValueError(f"Required field '{field}' missing from step configuration '{config.name}'")
            
        # Validate type-specific requirements in subclasses
        self._validate_config_impl(config)
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        """
        Implementation-specific validation. Should be overridden by subclasses.
        
        Args:
            config: The LinkConfig object to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Default implementation does nothing additional
        pass
    
    def get_required_fields(self) -> list:
        """Returns a list of required fields for this link."""
        # This method is deprecated - use config.get_required_fields() instead
        return LinkConfig.get_required_fields()
    
    def format_output(self, result: Any, success: bool = True, 
                     error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Formats the output according to the standard structure.
        
        Args:
            result: The raw result to format
            success: Whether the execution was successful
            error: Error message if any
            metadata: Additional metadata about the execution
            
        Returns:
            Dict[str, Any]: Standardized output dictionary
        """
        if metadata is None:
            metadata = {}
            
        # Add standard metadata
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "link_type": self.__class__.__name__
        })
        
        # Handle different result types
        if result is None and success:
            data = {}
        elif isinstance(result, dict) and not isinstance(result, LinkOutput):
            data = result
        elif isinstance(result, (str, int, float, bool, list)):
            data = {"result": result}
        else:
            # For complex objects, try to convert to dict if possible
            try:
                data = dict(result)
            except (TypeError, ValueError):
                data = {"result": str(result)}
        
        try:
            output = LinkOutput(
                success=success,
                data=result,
                error=error,
                metadata=metadata
            )
            return output.model_dump()
        except ValidationError as e:
            # If validation fails, return a simpler format
            return {
                "success": False,
                "data": {},
                "error": f"Output formatting error: {e}",
                "metadata": {"timestamp": datetime.now().isoformat()}
            }
    
    def execute(self, config: LinkConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Template method that defines the algorithm for executing a link.
        Accepts only a LinkConfig object.
        
        Args:
            config: A LinkConfig object
            context: Current execution context
            
        Returns:
            Dict[str, Any]: Standardized output dictionary
        """
        logging.info(f"Executing link: {self.__class__.__name__} with config: {config}")
        logging.debug("Link execution started with context: %s", context)
        start_time = datetime.now()
        link_type = self.__class__.__name__
        step_name = config.name
        
        try:
            # Validate inputs
            self.validate_config(config)
            
            # Execute implementation
            result = self._execute_impl(config, context)
            logger.trace("Raw result from _execute_impl: %s", result)
            
            # Process output schema if provided
            if config.output_schema:
                if isinstance(result, str):
                    logger.trace(f"Processing string output with schema for step: {step_name}")
                    processed_result = self._process_output_schema(result, config.output_schema, config, context)
                elif isinstance(result, dict):
                    logger.trace(f"Processing dictionary output with schema for step: {step_name}")
                    # For dictionaries, use the result directly as structured data if it matches the schema
                    # or transform it if needed
                    if "inputs" in result and isinstance(result["inputs"], dict):
                        # Special case for UserInputLink which returns {"inputs": {...}}
                        inputs = result["inputs"]
                        # Create case-insensitive maps
                        input_keys_map = {k.lower(): k for k in inputs.keys()}
                        schema_props = config.output_schema.get("properties", {})
                        
                        processed_result = {}
                        for schema_key in schema_props:
                            # Look for a case-insensitive match
                            if schema_key.lower() in input_keys_map:
                                # Use the actual case from the input
                                input_key = input_keys_map[schema_key.lower()]
                                processed_result[schema_key] = inputs[input_key]
                    else:
                        # No special handling needed
                        processed_result = {}
                else:
                    processed_result = {}
            else:
                processed_result = {}
            logger.trace("Processed result from _process_output_schema: %s", processed_result)
            
            # Create output data using raw and processed results
            output_data = OutputData(raw=result, json=processed_result)
            logger.trace("Constructed OutputData (data.json): %s", output_data.model_dump())
            
            # Calculate execution time and format output
            execution_time = (datetime.now() - start_time).total_seconds()
            formatted_output = self.format_output(
                result=output_data,
                metadata={"execution_time": execution_time}
            )
            logging.debug("Execution result: %s", formatted_output)
            return formatted_output
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_output = self.format_output(
                result=None,
                success=False,
                error=str(e),
                metadata={"execution_time": execution_time}
            )
            logging.debug("Execution error: %s", error_output)
            return error_output
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        """
        Implementation method to be overridden by subclasses.
        
        Args:
            config: The LinkConfig object for this step
            context: Current execution context
            
        Returns:
            Any: The result of the execution
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement _execute_impl")
    
    def _process_output_schema(self, raw_output: str, schema: Dict[str, Any], config: LinkConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert the raw output into a structured format based on the inline schema.
        This conversion is done by sending a prompt to an LLM which is instructed as follows:
        
        "Please do your best to populate this JSON schema with the text below:
        
        {json schema}
        
        {text}"
        
        The method returns a standardized structure that always includes the raw output under 'result'
        as well as the converted data.
        """
        import json
        from langchain_openai import ChatOpenAI
        
        print("DEBUG CHECK: Entering _process_output_schema")  # Basic print for debugging

        try:
            logger.trace(f"Processing output schema for step: {config.name}")
            logger.trace(f"- Schema: {schema}")
            logger.trace(f"- Raw output: {raw_output}")
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "title": f"Schema for {config.name}",
                "description": "Structured data extracted from the raw output",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
            
            conversion_prompt = (
                "Use the following schema to generate a json object that captures the information in the text below:\n\n"
                "===BEGIN SCHEMA===\n"
                f"{json.dumps(json_schema, indent=2)}\n"
                "===END SCHEMA===\n\n"
                f"Extract the information from this text:\n\n"
                "===BEGIN TEXT===\n"
                f"{raw_output}\n\n"
                "===END TEXT===\n\n"
                f"Return ONLY the JSON object with no additional text, explanation, or code blocks."
            )
            logger.trace(f"- Conversion prompt: {conversion_prompt}")

            try:
                llm = ChatOpenAI(model=config.model, temperature=config.temperature, max_tokens=config.max_tokens)
                response = llm.invoke(conversion_prompt)
                conversion_result = response.content.strip()
                logger.trace(f"- Conversion result: {conversion_result}")
                converted_data = self.parse_output_to_json(conversion_result)
            except Exception as e:
                converted_data = {}
            return converted_data
        except Exception as e:
            logger.error(f"Error processing output schema: {str(e)}")
            raise
    
    # Shared file handling methods
    
    def read_template_file(self, file_path: str) -> str:
        """
        Read a template file from disk.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            String content of the file
            
        Raises:
            ValueError: If file not found or error reading it
        """
        # First try to resolve as a prompt path if it's not absolute
        if not os.path.isabs(file_path):
            file_path = self.get_prompt_path(file_path)
            
        try:
            self._validate_file_path(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            raise ValueError(f"Template file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading template file '{file_path}': {str(e)}")
    
    def _validate_file_path(self, file_path: str) -> None:
        """
        Validate that a file path exists and is accessible.
        
        Args:
            file_path: Path to check
            
        Raises:
            ValueError: If path is invalid or file doesn't exist
        """
        if not file_path:
            raise ValueError("Empty file path provided")
        
        # Try to resolve relative paths against the prompt directory
        if not os.path.isabs(file_path) and not os.path.exists(file_path):
            prompt_path = self.get_prompt_path(file_path)
            if os.path.exists(prompt_path):
                # Silently update to the full path
                file_path = prompt_path
            
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
            
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
    
    def extract_parameters_from_template(self, template: str) -> List[str]:
        """
        Extract parameter names from a template string.
        
        Args:
            template: Template string with placeholders
                Supports both {param} and {{param}} formats
            
        Returns:
            List of parameter names found in the template
        """
        # Find all parameters in both formats
        brace_params = re.findall(r'\{\{([^{}]+)\}\}', template)

        unique_params = []
        for param in brace_params:
            if (param not in unique_params):
                unique_params.append(param)
        return unique_params

    def format_template_with_params(self, template: str, params: Dict[str, Any]) -> str:
        """
        Format a template string with provided parameters.
        Supports both {param} and {{param}} formats.
        Raises ValueError if a required parameter is missing.
        """
        # First check all required placeholders are present in our parameters.
        placeholder_pattern = re.compile(r'\{([^{}]+)\}')
        placeholders = placeholder_pattern.findall(template)
        missing = [p for p in placeholders if p not in params]
        if (missing):
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

        # Callback function to replace each placeholder with its value.
        def replacer(match):
            key = match.group(1)
            return str(params.get(key, match.group(0)))  # fallback returns original text

        # Replace placeholders using our custom substitution.
        formatted = placeholder_pattern.sub(replacer, template)

        # Handle double-brace placeholders (if any) as literal braces.
        # Replace occurrences of '{{' and '}}' with '{' and '}' respectively.
        formatted = formatted.replace('{{', '{').replace('}}', '}')
        return formatted
    
    def resolve_context_references(self, step_config: Dict[str, Any], context: Dict[str, Any], 
                                 param_key: str = "parameters") -> Dict[str, Any]:
        """
        Resolve parameters that reference context values like {{previous_step.output}}.
        
        Args:
            step_config: Step configuration dictionary
            context: Current execution context
            param_key: Key in step_config that contains parameters to resolve
            
        Returns:
            Dictionary with parameters resolved from context
        """
        if (param_key not in step_config):
            return {}
            
        resolved_params = {}
        param_count = len(step_config[param_key])
        
        for key, value in step_config[param_key].items():
            if (isinstance(value, str) and value.startswith('{{') and value.endswith('}}')):
                # Extract the reference path
                ref_path = value[2:-2].strip()
                # Split by dots to navigate nested objects
                path_parts = ref_path.split('.')
                
                # Find the base object in context
                if (path_parts[0] in context):
                    obj = context[path_parts[0]]
                    # Navigate through the nested path
                    for part in path_parts[1:]:
                        if (isinstance(obj, dict) and part in obj):
                            obj = obj[part]
                        elif (hasattr(obj, part)):
                            obj = getattr(obj, part)
                        else:
                            obj = None
                            break
                            
                    # Use the found value
                    resolved_params[key] = obj
                else:
                    resolved_params[key] = value  # Keep original as fallback
            else:
                # Not a reference, use as is
                resolved_params[key] = value
                
        return resolved_params
    
    def parse_output_to_json(self, output_text: str) -> Dict[str, Any]:
        """
        Parse potential JSON from LLM output, handling various formats.
        
        Args:
            output_text: Raw text that might contain JSON
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValueError: If JSON parsing fails
        """
        # Try direct parsing first
        logger.trace(f"🔍 Attempting to parse JSON from output: {output_text}")
        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            logger.trace("Direct JSON parsing failed")
            pass
            
        # Try to extract JSON from markdown code blocks
        logger.trace("Trying to extract JSON from code blocks")
        code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", output_text)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                logger.trace("JSON parsing from code block failed")
                pass
                
        # Try to extract just a JSON object with regex
        logger.trace("Trying to extract JSON object with regex")
        json_obj_match = re.search(r"\{[\s\S]*\}", output_text)
        if json_obj_match:
            try:
                return json.loads(json_obj_match.group(0))
            except json.JSONDecodeError:
                logger.trace("JSON parsing from object failed")
                pass
        
        logger.trace("Trying to extract JSON array with regex")
        json_array_match = re.search(r"\[[\s\S]*\]", output_text)
        if json_array_match:
            try:
                return json.loads(json_array_match.group(0))
            except json.JSONDecodeError:
                logger.trace("JSON parsing from array failed")
                pass
        logger.trace(f"Trying to extract JSON from text: {output_text}")
        fixed_text = output_text
        # Fix trailing commas in objects
        logger.trace(f"Fixing trailing commas in objects: {fixed_text}")
        fixed_text = re.sub(r",\s*}", "}", fixed_text)
        # Fix trailing commas in arrays
        logger.trace(f"Fixing trailing commas in arrays: {fixed_text}")
        fixed_text = re.sub(r",\s*\]", "]", fixed_text)
        # Add quotes around unquoted keys
        logger.trace(f"Adding quotes around unquoted keys: {fixed_text}")
        fixed_text = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed_text)
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            logger.trace("JSON parsing from fixed text failed")
            pass
            
        # As a last resort, try to search for any JSON-like structure
        logger.trace("Trying to extract JSON from any structure")
        for pattern in [r"\{[^{]*\}", r"\[[^[]*\]"]:
            matches = re.findall(pattern, output_text)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    logger.trace("JSON parsing from structure failed")
                    continue
                    
        # If all parsing attempts fail, raise an error
        raise ValueError(f"Failed to parse JSON from output: {output_text[:100]}...")
    
    def append_json_schema_to_prompt(self, prompt_text: str, schema: Dict[str, Any]) -> str:
        """
        Append a structured JSON schema to a prompt to guide LLM response format.
        
        Args:
            prompt_text: Original prompt text
            schema: JSON schema structure
            
        Returns:
            Prompt with schema instructions appended
        """
        schema_str = json.dumps(schema, indent=2)
        return (f"{prompt_text}\n\n"
                f"IMPORTANT: Your response MUST be formatted as valid JSON with this structure:\n"
                f"```json\n{schema_str}\n```\n\n"
                f"Ensure your response can be parsed as valid JSON.")
    
    @classmethod
    def get_config_schema(cls, config: LinkConfig) -> Dict[str, Any]:
        # Convenience method to access the schema from the config instance
        return config.get_schema()
    
    def resolve_placeholders_in_text(self, text: str, context: Dict[str, Any]) -> str:
        import re
        def replacer(match):
            placeholder = match.group(1)
            parts = placeholder.split(".")
            
            # Start with the first part from context
            value = context.get(parts[0], "")
            
            # Traverse the nested structure properly
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    logger.trace(f"Could not resolve path part '{part}' in placeholder '{placeholder}'")
                    value = ""
                    break
                    
            return str(value)
        return re.sub(r"{{([^{}]+)}}", replacer, text)
