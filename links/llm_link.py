import os
import logging
from typing import Dict, Any, Optional, List, Union, ClassVar, Callable
from pydantic import BaseModel, Field, field_validator, model_validator
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain as LangchainLLMChain
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.language_models import BaseLLM
from config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOKEN_LIMIT
from links.base_link import BaseLink, LinkConfig  # Import LinkConfig from base_link
import json

logger = logging.getLogger(__name__)

class TemplateConfig(BaseModel):
    """Configuration for template-based prompting."""
    file: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
class LLMLinkConfig(LinkConfig):
    """Extended configuration for LLM link with specific fields"""
    # Default constants
    DEFAULT_TYPE: ClassVar[str] = "llm"
    DEFAULT_MODEL: ClassVar[str] = DEFAULT_LLM_MODEL
    DEFAULT_TEMPERATURE: ClassVar[str] = DEFAULT_TEMPERATURE
    DEFAULT_MAX_TOKENS: ClassVar[str] = DEFAULT_TOKEN_LIMIT
    DEFAULT_OUTPUT_KEY: ClassVar[str] = "result"
    DEFAULT_EXECUTION_METHOD: ClassVar[str] = "direct"
    
    # Common fields with defaults
    model: str = Field(default_factory=lambda: LLMLinkConfig.DEFAULT_MODEL)
    temperature: float = Field(default_factory=lambda: LLMLinkConfig.DEFAULT_TEMPERATURE)
    max_tokens: int = Field(default_factory=lambda: LLMLinkConfig.DEFAULT_MAX_TOKENS)
    
    # Fields for direct prompt usage
    prompt: Optional[str] = None
    
    # Fields for template-based usage
    template: Optional[Union[str, TemplateConfig]] = None
    
    # Output configuration
    output_key: str = Field(default_factory=lambda: LLMLinkConfig.DEFAULT_OUTPUT_KEY)
    
    # Execution method
    execution_method: str = Field(default_factory=lambda: LLMLinkConfig.DEFAULT_EXECUTION_METHOD)  # 'direct' or 'chain'
    
    # Extend the required fields from parent class
    required_fields: ClassVar[List[str]] = LinkConfig.required_fields + ["model"]
    
    conversation: str = "default"  # new field to specify conversation id
    
    # Auto-set type if not provided
    @field_validator('type', mode='before')
    @classmethod
    def set_default_type(cls, v):
        return v or cls.DEFAULT_TYPE
    
    # Validate that either prompt or template is provided - using model validator
    @model_validator(mode='after')
    def check_prompt_or_template(self):
        if self.template is None and self.prompt is None:
            raise ValueError("Either 'prompt' or 'template' must be provided")
        return self

class LLMLink(BaseLink):
    """Link for LLM operations, supporting both direct prompts and templates."""
    
    def get_required_fields(self) -> list:
        """Returns list of required fields for LLM steps."""
        # Use the required fields from the config class
        return LLMLinkConfig.get_required_fields()
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        """
        Validate LLM link configuration.
        
        Args:
            config: The LinkConfig object to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Initialize validation variables
        has_direct_prompt = config.prompt is not None
        has_template = config.template is not None
        
        # Remove this problematic line
        # template_path = config.template if has_template else None
        
        parameters = config.parameters or {}
        
        # Check that either prompt or template exists
        if not (has_direct_prompt or has_template):
            raise ValueError("LLM step requires either 'prompt' or 'template' field")
        
        # If template is provided, validate the template file exists
        if has_template:
            template = config.template
            try:
                template_content = None
                template_file_path = None
                
                if isinstance(template, str):
                    template_file_path = template
                    self._validate_template_path(template_file_path)
                    # Read the template to validate parameters
                    template_content = self.read_template_file(self.get_prompt_path(template_file_path))
                    
                elif hasattr(template, 'file'):  # TemplateConfig object
                    template_file_path = template.file
                    self._validate_template_path(template_file_path)
                    # Read the template to validate parameters
                    template_content = self.read_template_file(self.get_prompt_path(template_file_path))
                    
                    # Check TemplateConfig.inputs instead of config.parameters
                    template_inputs = template.inputs or {}
                    required_params = self.extract_parameters_from_template(template_content)
                    missing_params = [p for p in required_params if p not in template_inputs]
                    
                    if missing_params:
                        raise ValueError(f"Missing parameters required by template: {', '.join(missing_params)}")
                    return  # Skip the check below since we already validated

                elif isinstance(template, dict) and 'file' in template:
                    template_file_path = template['file']
                    self._validate_template_path(template_file_path)
                    # Read the template to validate parameters
                    template_content = self.read_template_file(self.get_prompt_path(template_file_path))
                    
                    # Check dict.inputs instead of config.parameters
                    template_inputs = template.get('inputs', {})
                    required_params = self.extract_parameters_from_template(template_content)
                    missing_params = [p for p in required_params if p not in template_inputs]
                    
                    if missing_params:
                        raise ValueError(f"Missing parameters required by template: {', '.join(missing_params)}")
                    return  # Skip the check below since we already validated
                    
                else:
                    raise ValueError(f"Unsupported template format: {type(template)}")
                    
                # Only check parameters for string templates (not TemplateConfig objects)
                if isinstance(template, str) and template_content:
                    required_params = self.extract_parameters_from_template(template_content)
                    missing_params = [p for p in required_params if p not in parameters]
                    
                    if missing_params:
                        raise ValueError(f"Missing parameters required by template: {', '.join(missing_params)}")
                        
            except ValueError as e:
                raise ValueError(f"Template validation error: {str(e)}")
        
        elif has_direct_prompt:
            prompt = config.prompt
            
            # Validate parameters for direct prompt
            if prompt:
                required_params = self.extract_parameters_from_template(prompt)
                # Skip parameters with a dot (expected to be resolved from context)
                missing_params = [p for p in required_params if p not in parameters and '.' not in p]
                
                if missing_params:
                    raise ValueError(f"Missing parameters required by prompt: {', '.join(missing_params)}")
    
    def _validate_template_path(self, template_path: str) -> None:
        """Validate that the template path exists and is accessible."""
        # This will raise ValueError if file doesn't exist
        resolved_path = self.get_prompt_path(template_path)
        self._validate_file_path(resolved_path)
    
    def _get_llm(self, model: str, temperature: float, max_tokens: int) -> BaseLLM:
        """Helper method to create appropriate LLM based on model name."""
        if model.startswith("gpt-3.5") or model.startswith("gpt-4"):
            return ChatOpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            return OpenAI(model=model, temperature=temperature, max_tokens=max_tokens)
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        """
        Execute an LLM step using either direct prompt or template.
        
        Args:
            config: The LinkConfig object for this step
            context: Current execution context
            
        Returns:
            The LLM response
        """
        step_name = config.name
        
        # Extract configuration
        model_name = config.model or LLMLinkConfig.DEFAULT_MODEL
        temperature = config.temperature or LLMLinkConfig.DEFAULT_TEMPERATURE
        max_tokens = config.max_tokens or LLMLinkConfig.DEFAULT_MAX_TOKENS
        output_key = config.output_key or LLMLinkConfig.DEFAULT_OUTPUT_KEY
        execution_method = config.execution_method or LLMLinkConfig.DEFAULT_EXECUTION_METHOD
        
        # Process the prompt based on the provided configuration
        prompt_text = self._get_prompt_text(config, context)
        
        # Execute using appropriate method based on configuration
        if execution_method == "chain":
            result = self._execute_with_chain(
                formatted_prompt=prompt_text,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                output_key=output_key,
            )
        else:
            result = self._execute_directly(
                formatted_prompt=prompt_text,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                config=config,
                context=context
            )
        
        # Add metadata
        metadata = {
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "execution_method": execution_method,
            "prompt_tokens": len(prompt_text) // 4,  # Rough estimate
            "completion_tokens": len(str(result)) // 4 if isinstance(result, str) else 0  # Rough estimate
        }

        return result

    def _get_prompt_text(self, config: LinkConfig, context: Dict[str, Any]) -> str:
        """
        Get the prompt text based on the configuration.
        
        Args:
            config: The LinkConfig object
            context: Current execution context
            
        Returns:
            The formatted prompt text
        """
        # Check if we have a direct prompt
        if config.prompt is not None:
            prompt_text = self.resolve_placeholders_in_text(config.prompt, context)
            return prompt_text
        
        # Handle template configuration
        template = config.template
        
        # If template is a string, it's either a direct template or a file path
        if isinstance(template, str):
            if template.endswith((".txt", ".md", ".prompt")):
                # Load template from file
                template_path = self.get_prompt_path(template)
                template_content = self.read_template_file(template_path)
                prompt_text = self.resolve_placeholders_in_text(template_content, context)
                return prompt_text
            else:
                # Use the template string directly
                prompt_text = self.resolve_placeholders_in_text(template, context)
                return prompt_text
        
        # If template is a dictionary/TemplateConfig with 'file' field
        elif isinstance(template, dict) and "file" in template:
            # Load template from file
            template_path = self.get_prompt_path(template["file"])
            template_content = self.read_template_file(template_path)
            
            # Process template with its specific inputs
            inputs = template.get("inputs", {})
            resolved_inputs = {}
            
            # Resolve any placeholders in the inputs
            for key, value in inputs.items():
                if isinstance(value, str):
                    resolved_value = self.resolve_placeholders_in_text(value, context)
                    resolved_inputs[key] = resolved_value
                else:
                    resolved_inputs[key] = value
            prompt_text = self.format_template_with_params(template_content, resolved_inputs)
            return prompt_text
        
        # For TemplateConfig objects (Pydantic model)
        elif hasattr(template, "file"):
            # Load template from file
            template_path = self.get_prompt_path(template.file)
            template_content = self.read_template_file(template_path)
            
            # Process template with its specific inputs
            inputs = template.inputs or {}
            resolved_inputs = {}
            
            # Resolve any placeholders in the inputs
            for key, value in inputs.items():
                if isinstance(value, str):
                    resolved_inputs[key] = self.resolve_placeholders_in_text(value, context)
                else:
                    resolved_inputs[key] = value
            
            # Apply inputs to template
            prompt_text = self.format_template_with_params(template_content, resolved_inputs)
            return prompt_text
        
        raise ValueError(f"Invalid template configuration: {template}")
    
    def _execute_with_chain(self, formatted_prompt: str, model_name: str, 
                           temperature: float, max_tokens: int, output_key: str) -> Dict[str, Any]:
        """Execute using LangChain's LLMChain."""
        # Create the LLM
        llm = self._get_llm(model_name, temperature, max_tokens)
        
        # Create and run the LangChain LLMChain
        prompt_template = PromptTemplate.from_template(formatted_prompt)
        chain = LangchainLLMChain(llm=llm, prompt=prompt_template, output_key=output_key)
        result = chain.invoke({})  # No need to pass parameters as they're already in the formatted prompt
        return result
    
    def _execute_directly(self, formatted_prompt: str, model_name: str,
                         temperature: float, max_tokens: int,
                         config: LinkConfig, context: Dict[str, Any]) -> str:
        """Execute directly using the LLM model."""
        llm = self._get_llm(model=model_name, temperature=temperature, max_tokens=max_tokens)
        # Check if conversation is enabled (not "none")
        if getattr(config, "conversation", "default") != "none":
            conv_id = config.conversation or "default"
            # Initialize conversation logs in context if not present
            if "__conversation_logs__" not in context:
                context["__conversation_logs__"] = {}
            conv_logs = context["__conversation_logs__"].get(conv_id)
            if conv_logs is None:
                conv_logs = [{"role": "system", "content": "You are a helpful assistant."}]
                context["__conversation_logs__"][conv_id] = conv_logs
            # Append user message as the new turn
            conv_logs.append({"role": "user", "content": formatted_prompt})
            try:
                result_message = llm.invoke(conv_logs)
                # Assume result_message is an object with a 'content' attribute
                assistant_response = result_message.content.strip()
            except Exception as e:
                raise ValueError(f"LLM call failed: {str(e)}")
            # Append assistant response to the conversation log
            conv_logs.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        else:
            # No conversation handling, use direct prompt syntax
            try:
                result = llm.invoke(formatted_prompt)
                output = result.content.strip()
                return output
            except Exception as e:
                raise ValueError(f"LLM call failed: {str(e)}")
    
    def _create_schema_instruction(self, schema: Dict[str, Any]) -> str:
        """Create clear instructions for the LLM based on the schema."""
        properties = schema.get("properties", {}) if isinstance(schema, dict) else schema
        
        # Build a human-readable description of the expected format
        field_descriptions = []
        for field_name, field_def in properties.items():
            desc = field_def.get("description", f"The {field_name}")
            field_type = field_def.get("type", "string")
            field_descriptions.append(f"- '{field_name}' ({field_type}): {desc}")
        
        instructions = [
            "Please format your response as a JSON object with the following fields:",
            *field_descriptions,
            "",
            "IMPORTANT: Your response should be valid JSON that can be parsed directly."
        ]
        
        return "\n".join(instructions)
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate output against schema and reformat if needed."""
        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary output, got {type(data).__name__}")
        
        properties = schema.get("properties", {}) if isinstance(schema, dict) else schema
        result = {}
        
        # Process each field in the schema
        for field_name, field_def in properties.items():
            field_type = field_def.get("type", "string")
            
            # Check if the field exists in the output
            if field_name in data:
                value = data[field_name]
                # Basic type validation and conversion
                if field_type == "string" and not isinstance(value, str):
                    value = str(value)
                elif field_type == "number" and isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                result[field_name] = value
            else:
                # Field missing - try to find it with case-insensitive matching
                for key in data:
                    if key.lower() == field_name.lower():
                        result[field_name] = data[key]
                        break
        
        return result
