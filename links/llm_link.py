import logging
import os
from typing import Dict, Any, Optional, List, Union, ClassVar
from pydantic import BaseModel, Field, field_validator, model_validator
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain as LangchainLLMChain
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.language_models import BaseLLM
from config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOKEN_LIMIT
from links.base_link import BaseLink, LinkConfig  # Import LinkConfig from base_link

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
    template: Optional[str] = None
    
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
        logging.debug(f"MODEL VALIDATOR - Template: '{self.template}', Prompt: '{self.prompt}'")
        if self.template is None and self.prompt is None:
            logging.debug("MODEL VALIDATOR - Both template and prompt are None")
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
        template_path = config.template if has_template else None
        parameters = config.parameters or {}
        
        logging.debug(f"Config: {config}")
        logging.debug(f"Direct prompt: {has_direct_prompt}, Template: {has_template}")
        logging.debug(f"Template path: {template_path}")
        logging.debug(f"Parameters: {parameters}")
        logging.debug(f"Config type: {type(config).__name__}")
        logging.debug(f"Config fields: {dir(config)}")
        logging.debug(f"Has prompt: {hasattr(config, 'prompt')}, value: {getattr(config, 'prompt', None)}")
        logging.debug(f"Has template: {hasattr(config, 'template')}, value: {getattr(config, 'template', None)}")

        
        # Check that either prompt or template exists
        if not (has_direct_prompt or has_template):
            raise ValueError("LLM step requires either 'prompt' or 'template' field")
            
        if has_direct_prompt and has_template:
            logging.warning(f"Both 'prompt' and 'template' provided; 'template' will be used")
            
        # If template is provided, validate the template file exists
        if has_template and template_path:
            try:
                self._validate_template_path(template_path)
            except ValueError as e:
                raise ValueError(f"Template validation error: {str(e)}")
        
        # Check parameters that will be used in prompt formatting
        if has_template and template_path:
            logging.debug("Validating template parameters")
            try:
                # Try to resolve template path
                template_path = self.get_prompt_path(template_path)
                
                # Read the template to validate parameters
                template_content = self.read_template_file(template_path)
                required_params = self.extract_parameters_from_template(template_content)
                
                # Check if all parameters are provided
                missing_params = [p for p in required_params if p not in parameters]
                
                if missing_params:
                    raise ValueError(f"Missing parameters required by template: {', '.join(missing_params)}")
            except ValueError as e:
                logging.error(f"Template validation error: {str(e)}")
                raise ValueError(f"Template validation error: {str(e)}")
        
        elif has_direct_prompt:
            logging.debug("Validating direct prompt parameters")
            prompt = config.prompt
            
            # Validate parameters for direct prompt
            if prompt:
                required_params = self.extract_parameters_from_template(prompt)
                # Skip parameters with a dot (expected to be resolved from context)
                missing_params = [p for p in required_params if p not in parameters and '.' not in p]
                logging.debug(f"Required parameters for prompt: {required_params}")
                logging.debug(f"Missing parameters: {missing_params}")
                
                if missing_params:
                    raise ValueError(f"Missing parameters required by prompt: {', '.join(missing_params)}")
    
    def _validate_template_path(self, template_path: str) -> None:
        """Validate that the template path exists and is accessible."""
        # Additional debug info about the template path
        abs_path = os.path.abspath(template_path) if template_path else "None"
        prompt_dir_path = self.get_prompt_path(template_path) if template_path else "None"
        
        logging.debug(f"Template path validation:")
        logging.debug(f"  Original path: {template_path}")
        logging.debug(f"  Absolute path: {abs_path}")
        logging.debug(f"  Prompt directory path: {prompt_dir_path}")
        
        # List all files in the prompt directory for debugging
        prompt_dir = self.prompt_directory
        try:
            files = os.listdir(prompt_dir)
            logging.debug(f"Files in prompt directory ({prompt_dir}): {files}")
        except Exception as e:
            logging.debug(f"Could not list prompt directory: {e}")
        
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
        logging.info(f"🤖 Executing LLM step: {step_name}")
        
        # Extract configuration
        using_template = config.template is not None
        prompt_text = config.template if using_template else config.prompt
        model_name = config.model or LLMLinkConfig.DEFAULT_MODEL
        temperature = config.temperature or LLMLinkConfig.DEFAULT_TEMPERATURE
        max_tokens = config.max_tokens or LLMLinkConfig.DEFAULT_MAX_TOKENS
        output_key = config.output_key or LLMLinkConfig.DEFAULT_OUTPUT_KEY
        execution_method = config.execution_method or LLMLinkConfig.DEFAULT_EXECUTION_METHOD
        
        # Load template if needed
        if using_template and prompt_text.endswith((".txt", ".md", ".prompt")):
            template_path = self.get_prompt_path(prompt_text)
            logging.debug(f"Loading template from: {template_path}")
            prompt_text = self.read_template_file(template_path)
            logging.debug(f"Loaded template with {len(prompt_text)} characters")
        
        # --- Changed block: resolve placeholders directly from context ---
        try:
            formatted_prompt = self.resolve_placeholders_in_text(prompt_text, context)
            prompt_preview = formatted_prompt[:100] + ("..." if len(formatted_prompt) > 100 else "")
            logging.debug(f"Formatted prompt after placeholder replacement: {prompt_preview}")
        except Exception as e:
            logging.error(f"❌ Error replacing placeholders in prompt: {str(e)}")
            raise ValueError(f"Error replacing placeholders in prompt: {str(e)}")
        # --- End changed block ---
        
        # Apply output formatting if schema is provided
        output_format = config.output_format or "text"
        output_schema = config.output_schema
        
        if output_schema and output_format == "json":
            logging.debug(f"Appending JSON schema to prompt ({len(output_schema)} fields)")
            formatted_prompt = self.append_json_schema_to_prompt(formatted_prompt, output_schema)
        
        # Execute using appropriate method based on configuration
        if execution_method == "chain":
            result = self._execute_with_chain(
                formatted_prompt=formatted_prompt,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                output_key=output_key
            )
        else:
            result = self._execute_directly(
                formatted_prompt=formatted_prompt,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                config=config,
                context=context
            )
        
        # Parse output according to expected format
        if output_format == "json" and isinstance(result, str):
            logging.debug("Parsing output as JSON")
            try:
                result = self.parse_output_to_json(result)
                logging.debug(f"Successfully parsed JSON with {len(result) if isinstance(result, dict) else 0} keys")
            except ValueError as e:
                logging.error(f"❌ JSON parsing error: {str(e)}")
                raise ValueError(f"Error parsing JSON output: {str(e)}. Output was: {result}")
        
        # Add metadata
        metadata = {
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "execution_method": execution_method,
            "prompt_tokens": len(formatted_prompt) // 4,  # Rough estimate
            "completion_tokens": len(result) // 4 if isinstance(result, str) else 0  # Rough estimate
        }
        
        # Create output with standardized format
        if isinstance(result, dict) and output_key in result:
            # Result is already a dictionary with the expected key
            output = result
        else:
            # Wrap the raw result
            output = {output_key: result}
        
        return {"output": output, "metadata": metadata}
    
    def _execute_with_chain(self, formatted_prompt: str, model_name: str, 
                           temperature: float, max_tokens: int, output_key: str) -> Dict[str, Any]:
        """Execute using LangChain's LLMChain."""
        # Create the LLM
        llm = self._get_llm(model_name, temperature, max_tokens)
        
        # Create and run the LangChain LLMChain
        prompt_template = PromptTemplate.from_template(formatted_prompt)
        chain = LangchainLLMChain(llm=llm, prompt=prompt_template, output_key=output_key)
        
        logging.info(f"Running LLMChain with model: {model_name}, temp={temperature}")
        result = chain.invoke({})  # No need to pass parameters as they're already in the formatted prompt
        logging.debug(f"LLMChain result: {result}")
        
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
                logging.info(f"Sending conversation messages to {model_name} (conv_id: {conv_id})")
                result_message = llm.invoke(conv_logs)
                # Assume result_message is an object with a 'content' attribute
                assistant_response = result_message.content.strip()
            except Exception as e:
                logging.error(f"❌ Direct LLM call failed: {str(e)}")
                raise ValueError(f"LLM call failed: {str(e)}")
            # Append assistant response to the conversation log
            conv_logs.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        else:
            # No conversation handling, use direct prompt syntax
            try:
                logging.info(f"Sending prompt directly to {model_name} (no conversation)")
                result = llm.invoke(formatted_prompt)
                output = result.content.strip()
                output_preview = output[:100] + ("..." if len(output) > 100 else "")
                logging.info(f"✅ Received LLM response: {output_preview}")
                return output
            except Exception as e:
                logging.error(f"❌ Direct LLM call failed: {str(e)}")
                raise ValueError(f"LLM call failed: {str(e)}")