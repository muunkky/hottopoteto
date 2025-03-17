from typing import Dict, List, Any, Optional, Union
import yaml
import os
import json
import re
import random
import logging
import execjs
from datetime import datetime
from langchain_openai import ChatOpenAI
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, TemplateNotFound
from jsonschema import validate, ValidationError
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger(__name__)

# Define a TRACE level for detailed logging
TRACE = 15
logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kws, stacklevel=2)

logging.Logger.trace = trace

# Constants
MAX_CONVERSATION_LENGTH = 15
PROMPT_DIR = "prompts"

# Model classes for output types
class RecipeLinkOutput(BaseModel):
    """Base class for recipe link outputs."""
    raw: Optional[str] = Field(default=None, description="Raw, unprocessed output from the link")
    data: Dict[str, Any] = Field(default_factory=dict, description="Schema-driven JSON formatted output")
    
    def get_data(self, fallback_to_raw=True):
        """Get structured data, falling back to raw if needed and requested"""
        if self.data and len(self.data) > 0:
            return self.data
        elif fallback_to_raw and self.raw is not None:
            # Try to parse raw as JSON
            try:
                parsed = json.loads(extract_json(self.raw))
                return parsed
            except:
                return {"raw_content": self.raw}
        else:
            return {}

class UserInputOutput(RecipeLinkOutput):
    """Output schema for user input link."""
    pass

class LLMOutput(RecipeLinkOutput):
    """Output schema for LLM link."""
    pass

class FunctionOutput(RecipeLinkOutput):
    """Output schema for function link."""
    pass

# Utility functions
def build_context(memory: Dict[str, RecipeLinkOutput]) -> Dict[str, Any]:
    """
    Build a flattened context from memory.
    Each key is the sanitized link name (spaces replaced with underscores)
    with its output under the 'data' key. If the output contains a "raw_content"
    field that looks like JSON, try to parse it.
    """
    logger.trace("Building context from memory")
    context = {}
    for key, output_obj in memory.items():
        logger.trace(f"Processing memory key: {key}")
        # Create a representation with both raw and data fields
        context[key] = {
            "data": output_obj.data,
            "raw": output_obj.raw
        }
        data = output_obj.data
        if isinstance(data, dict) and "raw_content" in data:
            logger.trace(f"Found raw_content in {key}, attempting to parse as JSON")
            try:
                parsed = json.loads(data["raw_content"])
                logger.trace(f"Successfully parsed raw_content as JSON")
                context[key]["parsed_raw"] = parsed
            except Exception as e:
                logger.trace(f"Failed to parse raw_content as JSON: {e}")
                
        logger.trace(f"Added to context: {key} = (data: {type(data).__name__}, raw: {output_obj.raw is not None})")

    logger.trace(f"Built context with keys: {list(context.keys())}")
    return context

def attempt_fix_truncated_json(text: str) -> str:
    """
    Try to fix truncated or malformed JSON.
    This provides more advanced repairs than simple regex replacements.
    
    Args:
        text: Potentially truncated JSON text
        
    Returns:
        Repaired JSON string
    """
    logger.trace("Attempting to fix truncated/malformed JSON")
    # Extract text between first { and last }
    start_idx = text.find('{')
    if start_idx == -1:
        return text
        
    end_idx = text.rfind('}')
    if end_idx == -1:
        # No closing brace, try to add one
        return text[start_idx:] + "}"
        
    json_text = text[start_idx:end_idx+1]
    
    # Count opening and closing braces to check for balance
    opening_braces = json_text.count('{')
    closing_braces = json_text.count('}')
    
    # Add missing closing braces if needed
    if opening_braces > closing_braces:
        logger.trace(f"Adding {opening_braces - closing_braces} missing closing braces")
        json_text += "}" * (opening_braces - closing_braces)
    
    # Add missing opening braces if needed (less common)
    elif closing_braces > opening_braces:
        logger.trace(f"Adding {closing_braces - opening_braces} missing opening braces")
        json_text = "{" * (closing_braces - opening_braces) + json_text
    
    # Fix common issues that break JSON parsing
    json_text = fix_common_json_errors(json_text)
    
    return json_text

def fix_common_json_errors(text: str) -> str:
    """Fix common errors in JSON strings."""
    fixed = text
    
    # Fix missing quotes around string values
    fixed = re.sub(
        r':\s*(?![\[\{\"]|true|false|null|[0-9])([^,\}\]]+)([,\}\]])',
        r': "\1"\2',
        fixed
    )
    
    # Fix single quotes used instead of double quotes
    single_quoted_keys = re.findall(r"'([^']+)':", fixed)
    for key in single_quoted_keys:
        fixed = fixed.replace(f"'{key}':", f'"{key}":')
        
    # Fix JavaScript-style comments
    fixed = re.sub(r'//.*?\n', '', fixed)
    fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
    
    # Fix unquoted keys
    fixed = re.sub(r'([{,])\s*([a-zA-Z0-9_]+):', r'\1"\2":', fixed)
    
    # Fix trailing commas
    fixed = re.sub(r',\s*([\}\]])', r'\1', fixed)
    
    return fixed

def extract_json(text: str) -> str:
    """
    Extract JSON from text using multiple strategies in a cascading approach.
    This is far more resilient than simple regex extraction.
    
    Args:
        text: Text that might contain JSON
        
    Returns:
        String containing valid JSON or the original text if extraction fails
    """
    logger.trace(f"🔍 Attempting to extract JSON from text: {text[:200]}...")
    
    # If it's already a dict, convert to JSON string
    if isinstance(text, dict):
        logger.trace("Input is already a dictionary, converting to JSON string")
        return json.dumps(text)
        
    # Return empty dict for empty input
    if not text or not text.strip():
        logger.trace("Input is empty, returning empty object")
        return "{}"
        
    # Store the original text for fallback
    original_text = text
    
    # STRATEGY 1: Try direct parsing
    try:
        logger.trace("Trying direct JSON parsing")
        json.loads(text)
        logger.trace("Direct parsing succeeded")
        return text  # Already valid JSON
    except json.JSONDecodeError:
        logger.trace("Direct JSON parsing failed")
        pass
        
    # STRATEGY 2: Extract from markdown code blocks
    logger.trace("Trying to extract JSON from code blocks")
    code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    code_block_match = re.search(code_block_pattern, text)
    if (code_block_match):
        try:
            json_text = code_block_match.group(1)
            logger.trace(f"Found code block: {json_text[:100]}...")
            json.loads(json_text)
            logger.trace("JSON in code block is valid")
            return json_text
        except json.JSONDecodeError:
            logger.trace("JSON parsing from code block failed")
            pass
            
    # STRATEGY 3: Extract JSON object with regex
    logger.trace("Trying to extract JSON object with regex")
    json_obj_matches = re.finditer(r"\{[\s\S]*?\}", text)
    for match in json_obj_matches:
        try:
            json_text = match.group(0)
            logger.trace(f"Found potential JSON object: {json_text[:100]}...")
            json.loads(json_text)
            logger.trace("Found valid JSON object")
            return json_text
        except json.JSONDecodeError:
            logger.trace("JSON object not valid, trying next match")
            continue
    
    # STRATEGY 4: Extract JSON array with regex
    logger.trace("Trying to extract JSON array with regex")
    json_array_match = re.search(r"\[[\s\S]*?\]", text)
    if json_array_match:
        try:
            json_text = json_array_match.group(0)
            logger.trace(f"Found potential JSON array: {json_text[:100]}...")
            json.loads(json_text)
            logger.trace("Found valid JSON array")
            return json_text
        except json.JSONDecodeError:
            logger.trace("JSON array not valid")
            pass
            
    # STRATEGY 5: Fix common JSON errors
    logger.trace("Trying to fix common JSON errors")
    fixed_text = text
    
    # Remove markdown fences if any left
    if "```" in fixed_text:
        logger.trace("Removing markdown code fences")
        fixed_text = re.sub(r'```(?:json)?\s*', '', fixed_text)
        fixed_text = re.sub(r'\s*```', '', fixed_text)
    
    # Fix trailing commas in objects
    logger.trace("Fixing trailing commas in objects")
    fixed_text = re.sub(r",\s*}", "}", fixed_text)
    
    # Fix trailing commas in arrays
    logger.trace("Fixing trailing commas in arrays")
    fixed_text = re.sub(r",\s*\]", "]", fixed_text)
    
    # Add quotes around unquoted keys
    logger.trace("Adding quotes around unquoted keys")
    fixed_text = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed_text)
    
    # Try parsing the fixed text
    try:
        logger.trace("Trying to parse fixed text")
        json.loads(fixed_text)
        logger.trace("Fixed text is valid JSON")
        return fixed_text
    except json.JSONDecodeError:
        logger.trace("Fixed text still not valid JSON")
        pass
        
    # STRATEGY 6: Extract the first JSON-like structure with balanced braces
    logger.trace("Trying to extract JSON with balanced brace matching")
    try:
        # Simple balanced brace matching
        open_brace_pos = text.find('{')
        if open_brace_pos >= 0:
            depth = 0
            for i in range(open_brace_pos, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        # Found closing brace with balanced nesting
                        json_text = text[open_brace_pos:i+1]
                        try:
                            json.loads(json_text)
                            logger.trace("Found valid JSON using brace balancing")
                            return json_text
                        except:
                            logger.trace("Balanced braces don't contain valid JSON")
                            break
    except Exception as e:
        logger.trace(f"Error during brace matching: {e}")
        pass
        
    # STRATEGY 7: Fall back to the legacy method (attempt_fix_truncated_json)
    logger.trace("Attempting to fix truncated JSON")
    if '{' in text:
        json_text = attempt_fix_truncated_json(text)
        try:
            json.loads(json_text)
            logger.trace("Found valid JSON after fixing truncation")
            return json_text
        except json.JSONDecodeError:
            logger.trace("JSON still not valid after fixing truncation")
            pass
    
    # If all else fails, return the original text
    logger.trace("All extraction strategies failed, returning original text")
    return original_text

# Function registry
class FunctionRegistry:
    """Registry for functions callable from recipes."""
    
    _functions = {}
    
    @classmethod
    def register(cls, name, func, meta=None):
        """Register a function."""
        cls._functions[name] = {
            'function': func,
            'metadata': meta or {}
        }
    
    @classmethod
    def get(cls, name):
        """Get a registered function."""
        if name not in cls._functions:
            return None
        return cls._functions[name]['function']

# Main executor class
class RecipeExecutor:
    """Generic recipe executor that can work with any domain."""
    
    def __init__(self, recipe_path: str, domain: str = None):
        """Initialize with recipe path and optional domain."""
        self.recipe_path = recipe_path
        
        # Load the recipe
        with open(recipe_path, 'r') as f:
            self.recipe = yaml.safe_load(f)
            
        # Determine domain from recipe if not specified
        self.domain = domain or self.recipe.get("domain", "generic")
        
        # Initialize handlers
        self._init_handlers()
        
    def _init_handlers(self):
        """Initialize link handlers."""
        # Set up environment for templates
        self.env = Environment(
            loader=FileSystemLoader(PROMPT_DIR),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Initialize memory for storing link outputs
        self.memory = {}
        
        # Initialize function registry with default functions
        # TODO: make this configurable/scalable with a broad set of standard functions
        self.function_registry = {
            "random_number": self._function_random_number
        }
        
        # Add any domain-specific handlers if available
        if self.domain != "generic":
            try:
                from ..domains import get_domain_processor
                processor = get_domain_processor(self.domain)
                domain_functions = processor.get_functions()
                self.function_registry.update(domain_functions)
            except (ImportError, AttributeError):
                logger.warning(f"No function registry found for domain: {self.domain}")
    
    def _function_random_number(self, min_value=1, max_value=3):
        """Generate a random integer between min_value and max_value."""
        return {"num_events": random.randint(min_value, max_value)}
        
    def execute(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the recipe and return the result."""
        # Initialize inputs
        inputs = inputs or {}
        
        # Execute recipe links in sequence
        result = {}
        
        # Process links in order - handle both list and dictionary formats
        links = self.recipe.get("links", [])
        
        # Convert links from list to dictionary if needed
        links_dict = {}
        if isinstance(links, list):
            for link in links:
                name = link.get("name", f"Link_{len(links_dict)}")
                links_dict[name] = link
        else:
            links_dict = links
        
        # Check for circular dependencies in prompts before execution

        # TODO: Check if this code is necessary at all. Circular dependencies
        # should not be possible. The circular dependencies are caused during
        # the json parsing logic (repeat attempts to parse and repair the same text)
        dependency_graph = {}
        for link_name, link_config in links_dict.items():
            if link_config.get("type") == "llm":
                dependencies = []
                
                # Check prompt for references
                if "prompt" in link_config:
                    prompt = link_config["prompt"]
                    for other_link in links_dict:
                        if other_link != link_name and f"{{{{ {other_link}" in prompt:
                            dependencies.append(other_link)
                
                # Check template inputs for references
                elif "template" in link_config and "inputs" in link_config["template"]:
                    for input_val in link_config["template"]["inputs"].values():
                        if isinstance(input_val, str):
                            for other_link in links_dict:
                                if other_link != link_name and f"{{{{ {other_link}" in input_val:
                                    dependencies.append(other_link)
                
                dependency_graph[link_name] = dependencies
        
        # Check for cycles in the dependency graph
        visited = set()
        temp_visited = set()
        
        def has_cycle(node, path=None):
            if path is None:
                path = []
            
            if node in temp_visited:
                cycle_path = " -> ".join(path + [node])
                raise Exception(f"Circular dependency detected: {cycle_path}")
            
            if node in visited:
                return False
            
            temp_visited.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                if has_cycle(neighbor, path):
                    return True
            
            temp_visited.remove(node)
            visited.add(node)
            path.pop()
            return False
        
        # Check each node for cycles
        for node in dependency_graph:
            has_cycle(node)
        
        # Process links in order
        for link_name, link_config in links_dict.items():
            link_type = link_config.get("type")
            link_config["name"] = link_name
            
            # Execute link based on type
            link_output = self._execute_link(link_config)
                
            # Store link output in memory
            self.memory[link_name] = link_output
            result[link_name] = link_output
                
        return result

    def _get_domain_processor(self):
        """Get the appropriate domain processor based on recipe domain."""
        if not hasattr(self, 'domain') or not self.domain:
            return None
            
        try:
            # Import here to avoid circular imports
            from ..domains import get_domain_processor
            return get_domain_processor(self.domain)
        except (ImportError, ValueError):
            return None

    def _execute_function_link(self, link: Dict[str, Any]) -> FunctionOutput:
        """Execute a function link in the recipe."""
        logging.info(f"Executing function: {link['name']}")
        
        # Process inputs
        inputs = self._process_function_inputs(link)
        
        # Check if this is a registry function or direct code
        if "function" in link:
            function_config = link["function"]
            
            # CASE 1: Directly provided code
            if "code" in function_config:
                language = function_config.get("language", "python")  # Default to Python
                
                if language.lower() == "python":
                    # Execute Python code directly
                    try:
                        # Create a safe namespace for evaluation
                        safe_builtins = {
                            'abs': abs, 'all': all, 'any': any, 'bool': bool,
                            'dict': dict, 'float': float, 'int': int, 'len': len,
                            'list': list, 'max': max, 'min': min, 'range': range,
                            'round': round, 'sorted': sorted, 'str': str, 'sum': sum
                        }
                        local_vars = {**inputs}
                        
                        # Add ONLY safe random functions
                        # TODO: see how this relates to the
                        # function registry. Is it redundant?
                        local_vars['random_int'] = random.randint
                        local_vars['random_choice'] = random.choice
                        local_vars['random_sample'] = random.sample
                        
                        # Execute the code with restricted builtins
                        result = eval(
                            function_config["code"], 
                            {"__builtins__": safe_builtins}, 
                            local_vars
                        )
                        
                        # Ensure result is a dict
                        if not isinstance(result, dict):
                            result = {"result": result}
                            
                        logging.info(f"Python function result: {result}")
                        return FunctionOutput(data=result)
                    except Exception as e:
                        logging.error(f"Error executing Python function: {e}")
                        return FunctionOutput(data={"error": str(e), "security_note": "Execution restricted for security reasons"})
                elif language.lower() == "javascript":
                    # Handle JavaScript execution
                    try:
                        js_code = function_config["code"]
                        
                        # Create a JavaScript context with input parameters
                        inputs_json = json.dumps(inputs)
                        js_context = f"""
                        const inputs = {inputs_json};
                        function execute() {{
                            const min_value = inputs.min_value || 1;
                            const max_value = inputs.max_value || 3;
                            {js_code}
                        }}
                        execute();
                        """
                        
                        # Execute the JavaScript code
                        ctx = execjs.compile(js_context)
                        result = ctx.eval("execute()")
                        
                        # If result is not a dict, wrap it
                        if not isinstance(result, dict):
                            if function_config.get("name") == "random_number":
                                result = {"num_events": result}
                            else:
                                result = {"result": result}
                                
                        logging.info(f"JS Function result: {result}")
                        return FunctionOutput(data=result)
                        
                    except Exception as e:
                        logging.error(f"Error executing JavaScript function: {e}")
                        return FunctionOutput(data={"error": str(e)})
            
            # CASE 2: Registry function reference
            elif "name" in function_config:
                function_name = function_config["name"]
                
                # Try internal registry first
                if function_name in self.function_registry:
                    try:
                        result = self.function_registry[function_name](**inputs)
                        logging.info(f"Registry function result: {result}")
                        return FunctionOutput(data=result)
                    except Exception as e:
                        logging.error(f"Error executing function {function_name}: {e}")
                        return FunctionOutput(data={"error": str(e)})
                
                # Try global registry next
                func = FunctionRegistry.get(function_name)
                if func:
                    try:
                        result = func(**inputs)
                        logging.info(f"Global registry function result: {result}")
                        return FunctionOutput(data=result)
                    except Exception as e:
                        logging.error(f"Error executing function {function_name}: {e}")
                        return FunctionOutput(data={"error": str(e)})
        
        # Default fallback handling
        logging.error("Invalid function configuration")
        return FunctionOutput(data={"error": "Invalid function configuration"})

    def _process_function_inputs(self, link: Dict[str, Any]) -> Dict[str, Any]:
        """Process inputs for a function link, handling template references and defaults."""
        logger.trace(f"Processing function inputs for link: {link['name']}")
        
        inputs = {}
        if "inputs" not in link:
            logger.trace("No inputs defined for this function")
            return inputs
        
        base_context = build_context(self.memory)
        
        for key, input_config in link["inputs"].items():
            logger.trace(f"Processing input '{key}'")
            
            # Handle different input configurations
            if isinstance(input_config, dict):
                # Static configuration with possible default
                if "value" in input_config:
                    inputs[key] = input_config["value"]
                elif "default" in input_config:
                    inputs[key] = input_config["default"]
                else:
                    inputs[key] = None
            elif isinstance(input_config, str) and "{{" in input_config and "}}" in input_config:
                # It's a Jinja template reference
                try:
                    t = self.env.from_string(input_config)
                    rendered_val = t.render(**base_context)
                    inputs[key] = rendered_val
                except Exception as e:
                    logging.error(f"Error rendering input for key '{key}': {e}")
                    inputs[key] = None
            else:
                # Direct static value
                inputs[key] = input_config
        
        return inputs

    def _execute_llm_link(self, link: Dict[str, Any]) -> LLMOutput:
        logging.info(f"Executing LLM link: {link['name']}")
        
        model_name = link.get('model', "gpt-4o")
        temperature = link.get('temperature', 0.0)
        token_limit = link.get('token_limit', 512)
        output_schema = link.get('output_schema', None)
        
        base_context = build_context(self.memory)
        
        try:
            # Get formatted prompt - allow exceptions to propagate upward
            formatted_prompt = self._get_formatted_prompt(link, base_context)
            if not formatted_prompt:
                return LLMOutput(data={"error": "Failed to format prompt"})
        except Exception as e:
            error_str = str(e)
            # Re-raise missing template or circular dependency errors
            if "Template file not found" in error_str or "Circular dependency" in error_str:
                raise
            return LLMOutput(data={"error": error_str})
        
        # Check if conversation management is enabled
        conversation_mode = link.get('conversation', 'none')
        
        # Initialize conversation logs if needed
        if '__conversations' not in self.memory:
            self.memory['__conversations'] = {}
            
        if conversation_mode != 'none':
            conversation_id = conversation_mode if conversation_mode != 'default' else 'default'
            logger.trace(f"Using conversation mode with ID: {conversation_id}")
            
            # Initialize this conversation if it doesn't exist
            if conversation_id not in self.memory['__conversations']:
                self.memory['__conversations'][conversation_id] = [
                    {"role": "system", "content": "You are a helpful AI assistant."}
                ]
                
            # Get the conversation history
            conversation = self.memory['__conversations'][conversation_id]
            
            # Add the current prompt as a user message
            conversation.append({"role": "user", "content": formatted_prompt})
            
            # Create ChatOpenAI with conversation history
            llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=token_limit)
            
            try:
                response = llm.invoke(conversation)
                raw_result = response.content
                
                # Process the result
                result = {"raw": raw_result}
                
                # First, check if we have a simple value response (not JSON)
                if output_schema and "properties" in output_schema and "required" in output_schema:
                    # Try to handle simple responses (single number, word, etc.)
                    clean_result = raw_result.strip()
                    required_props = output_schema.get("required", [])
                    
                    # Check if this might be a simple value response
                    if len(required_props) == 1 and not (clean_result.startswith('{') or clean_result.startswith('[')):
                        try:
                            # Try to detect the type
                            prop_name = required_props[0]
                            prop_schema = output_schema["properties"].get(prop_name, {})
                            prop_type = prop_schema.get("type", "string")
                            
                            # Convert to appropriate type
                            if prop_type == "integer" and clean_result.isdigit():
                                value = int(clean_result)
                            elif prop_type == "number" and clean_result.replace('.', '', 1).isdigit():
                                value = float(clean_result)
                            elif prop_type == "boolean" and clean_result.lower() in ("true", "false", "yes", "no", "1", "0"):
                                value = clean_result.lower() in ("true", "yes", "1")
                            else:
                                value = clean_result
                            
                            # Create a proper dictionary with the schema's required property
                            result["data"] = {prop_name: value}
                            return LLMOutput(raw=result.get("raw"), data=result.get("data", {}))
                        except Exception as e:
                            logger.trace(f"Failed to convert simple response: {e}")
                            # Continue with normal JSON extraction
                
                # Add the response to conversation history
                conversation.append({"role": "assistant", "content": raw_result})
                
                # Add conversation pruning
                if len(conversation) > MAX_CONVERSATION_LENGTH:
                    # Keep system prompt + most recent messages
                    conversation = conversation[:1] + conversation[-(MAX_CONVERSATION_LENGTH-1):]
                
                # Parse with schema if provided
                if output_schema:
                    try:
                        extracted = extract_json(raw_result)
                        parsed = json.loads(extracted)
                        validate(instance=parsed, schema=output_schema)
                        result["data"] = parsed
                    except (json.JSONDecodeError, ValidationError) as e:
                        # Use schema processor
                        result["data"] = self._process_output_schema(raw_result, output_schema, base_context)
                else:
                    # No schema, use raw content
                    result["data"] = {"raw_content": raw_result}
                    
                return LLMOutput(raw=result.get("raw"), data=result.get("data", {}))
                
            except Exception as e:
                logging.error(f"Error invoking LLM: {e}")
                return LLMOutput(raw=f"Error: {str(e)}", data={"error": str(e)})
        else:
            # Direct LLM invocation without conversation history
            try:
                llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=token_limit)
                response = llm.invoke(formatted_prompt)
                raw_result = response.content
                
                # Process the result
                result = {"raw": raw_result}
                
                # First, check if we have a simple value response (not JSON)
                if output_schema and "properties" in output_schema and "required" in output_schema:
                    # Try to handle simple responses (single number, word, etc.)
                    clean_result = raw_result.strip()
                    required_props = output_schema.get("required", [])
                    
                    # Check if this might be a simple value response
                    if len(required_props) == 1 and not (clean_result.startswith('{') or clean_result.startswith('[')):
                        try:
                            # Try to detect the type
                            prop_name = required_props[0]
                            prop_schema = output_schema["properties"].get(prop_name, {})
                            prop_type = prop_schema.get("type", "string")
                            
                            # Convert to appropriate type
                            if prop_type == "integer" and clean_result.isdigit():
                                value = int(clean_result)
                            elif prop_type == "number" and clean_result.replace('.', '', 1).isdigit():
                                value = float(clean_result)
                            elif prop_type == "boolean" and clean_result.lower() in ("true", "false", "yes", "no", "1", "0"):
                                value = clean_result.lower() in ("true", "yes", "1")
                            else:
                                value = clean_result
                            
                            # Create a proper dictionary with the schema's required property
                            result["data"] = {prop_name: value}
                            return LLMOutput(raw=result.get("raw"), data=result.get("data", {}))
                        except Exception as e:
                            logger.trace(f"Failed to convert simple response: {e}")
                            # Continue with normal JSON extraction
                
                # Parse with schema if provided
                if output_schema:
                    try:
                        extracted = extract_json(raw_result)
                        parsed = json.loads(extracted)
                        validate(instance=parsed, schema=output_schema)
                        result["data"] = parsed
                    except (json.JSONDecodeError, ValidationError) as e:
                        # Use schema processor
                        result["data"] = self._process_output_schema(raw_result, output_schema, base_context)
                else:
                    # No schema, use raw content
                    result["data"] = {"raw_content": raw_result}
                    
                return LLMOutput(raw=result.get("raw"), data=result.get("data", {}))
                
            except Exception as e:
                logging.error(f"Error invoking LLM: {e}")
                return LLMOutput(raw=f"Error: {str(e)}", data={"error": str(e)})

    def _get_formatted_prompt(self, link: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Get a formatted prompt from either template file or direct prompt."""
        if "template" in link:
            try:
                template_file = link['template']['file']
                jinja_template = self.env.get_template(template_file)
                
                inputs_context = {}
                if 'inputs' in link['template']:
                    for key, raw_val in link['template']['inputs'].items():
                        try:
                            t = self.env.from_string(raw_val)
                            rendered_val = t.render(**context)
                            inputs_context[key] = rendered_val
                        except Exception as e:
                            logging.error(f"Error rendering input for key '{key}': {e}")
                            inputs_context[key] = ""
                            
                combined_context = {**context, **inputs_context}
                return jinja_template.render(**combined_context)
                
            except (TemplateNotFound, FileNotFoundError) as e:
                logging.error(f"Template file not found: {e}")
                raise Exception(f"Template file not found: {template_file}")
            except Exception as e:
                logging.error(f"Error loading/rendering template: {e}")
                raise Exception(f"Error loading/rendering template: {e}")
                
        elif "prompt" in link:
            # Process direct prompt as a Jinja template
            try:
                prompt_template = self.env.from_string(link["prompt"])
                return prompt_template.render(**context)
            except Exception as e:
                logging.error(f"Error rendering prompt: {e}")
                
                # Check for potential circular references which could lead to infinite loops
                error_str = str(e)
                if "is undefined" in error_str:
                    # This could be due to circular reference between links
                    if any(key in error_str for key in self.memory.keys()):
                        raise Exception(f"Possible circular reference in template: {e}")
                
                return ""
                
        logging.error("LLM link has neither a 'template' nor a 'prompt'.")
        return ""

    def _process_output_schema(self, raw_output: str, schema: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw LLM output into structured data conforming to schema."""
        conversion_prompt = (
            "Use the following schema to generate a JSON object that captures the information in the text below:\n\n"
            "===BEGIN SCHEMA===\n"
            f"{json.dumps(schema, indent=2)}\n"
            "===END SCHEMA===\n\n"
            f"Extract the information from this text:\n\n"
            "===BEGIN TEXT===\n"
            f"{raw_output}\n\n"
            "===END TEXT===\n\n"
            f"Return ONLY the JSON object with no additional text, explanation, or code blocks."
        )
        
        try:
            # Use a more constrained model for structured data extraction
            llm = ChatOpenAI(model_name="gpt-4o", temperature=0.0)
            response = llm.invoke(conversion_prompt)
            structured_text = response.content
            
            # Try to extract valid JSON
            extracted = extract_json(structured_text)
            structured_data = json.loads(extracted)
            
            return structured_data
        except Exception as e:
            logging.error(f"Error during schema processing: {e}")
            return {}

    def _execute_link(self, link_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a link with any registered link handler."""
        link_type = link_config.get("type")
        
        # Check if we have a handler for this link type
        try:
            from .links import get_link_handler
            handler = get_link_handler(link_type)
            
            # Build context from memory
            context = build_context(self.memory)
            
            # Execute the link using its handler
            return handler.execute(link_config, context)
            
        except ImportError:
            # Fall back to built-in link types
            if link_type == "llm":
                return self._execute_llm_link(link_config)
            elif link_type == "function":
                return self._execute_function_link(link_config)
            elif link_type == "user_input":
                return self._execute_user_input_link(link_config)
            else:
                raise ValueError(f"Unknown link type: {link_type}")

class TerminateProcessException(Exception):
    """Custom exception to signal termination of the recipe process."""
    def __init__(self, message="Process terminated by function"):
        self.message = message
        super().__init__(self.message)
