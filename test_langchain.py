import os
import yaml
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import re
from dotenv import load_dotenv
import logging
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError
import jsonschema
from jsonschema import validate, ValidationError
import hashlib
import random
from datetime import datetime
import execjs

MAX_CONVERSATION_LENGTH = 15

# Define a custom logging level
TRACE = 15  # Between DEBUG (10) and INFO (20)
logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kws, stacklevel=2)

logging.Logger.trace = trace

# Set up logging for our own code (only INFO level for prompt/response)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("langchain_openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def set_trace_logging(enable=False):
    """Enable or disable trace logging."""
    level = TRACE if enable else logging.INFO
    logging.getLogger(__name__).setLevel(level)
    
# Set to True during debugging sessions
set_trace_logging(False)  # Toggle to True when debugging

load_dotenv()

PROMPT_DIR = "prompts"

env = Environment(
    loader=FileSystemLoader(PROMPT_DIR),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True
)

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
    data: Dict[str, Any]

class LLMOutput(RecipeLinkOutput):
    """Output schema for LLM link."""
    data: Dict[str, Any]

class FunctionOutput(RecipeLinkOutput):
    """Output schema for function link."""
    data: Dict[str, Any]

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
                        json_text = text[open_brace_pos:i+1]
                        try:
                            json.loads(json_text)
                            logger.trace("Found valid JSON with brace matching")
                            return json_text
                        except json.JSONDecodeError:
                            logger.trace("JSON with brace matching not valid")
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
    # This regex looks for patterns like: "key": value, where value isn't true/false/null/number
    fixed = re.sub(
        r':\s*(?![\[\{\"]|true|false|null|[0-9])([^,\}\]]+)([,\}\]])',
        r': "\1"\2',
        fixed
    )
    
    # Fix single quotes used instead of double quotes (common LLM mistake)
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

class TerminateProcessException(Exception):
    """Custom exception to signal termination of the recipe process."""
    def __init__(self, message="Process terminated by function"):
        self.message = message
        super().__init__(self.message)

class LinkHandler:
    """Base class for all link handlers"""
    def execute(self, link: Dict[str, Any], memory: Dict[str, RecipeLinkOutput]) -> RecipeLinkOutput:
        """Execute a link and return its output"""
        raise NotImplementedError("Subclasses must implement execute()")

class EldorianWordRecipe:
    """
    A class to execute the Eldorian word generation recipe defined in a YAML file.
    """
    class LLMLinkHandler(LinkHandler):
        def __init__(self, recipe):
            self.recipe = recipe
            
        def execute(self, link: Dict[str, Any], memory: Dict[str, RecipeLinkOutput]) -> LLMOutput:
            return self.recipe._execute_llm_link(link)
            
    class UserInputLinkHandler(LinkHandler):
        def __init__(self, recipe):
            self.recipe = recipe
            
        def execute(self, link: Dict[str, Any], memory: Dict[str, RecipeLinkOutput]) -> UserInputOutput:
            return self.recipe._execute_user_input_link(link)
            
    class FunctionLinkHandler(LinkHandler):
        def __init__(self, recipe):
            self.recipe = recipe
            
        def execute(self, link: Dict[str, Any], memory: Dict[str, RecipeLinkOutput]) -> FunctionOutput:
            return self.recipe._execute_function_link(link)

    def __init__(self, recipe_path: str):
        with open(recipe_path, 'r') as f:
            self.recipe = yaml.safe_load(f)
        self.links = self.recipe['links']
        self.memory: Dict[str, RecipeLinkOutput] = {}
        # Configure Jinja2 environment to error on undefined variables
        self.env = Environment(
            loader=FileSystemLoader(PROMPT_DIR),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.prompt_history = []  # Initialize prompt history

        # Initialize link handler registry with proper references to self
        self.link_registry = {
            "llm": self.LLMLinkHandler(self),
            "user_input": self.UserInputLinkHandler(self),
            "function": self.FunctionLinkHandler(self)
        }

        # Initialize function registry
        self.function_registry = {
            "random_number": self._function_random_number,
            "syllable_generator": self._function_syllable_generator,
            "terminate_process": self._function_terminate_process
        }

    def register_link_handler(self, link_type: str, handler: LinkHandler) -> None:
        """Register a new link handler."""
        self.link_registry[link_type] = handler
        
    def get_link_handler(self, link_type: str) -> LinkHandler:
        """Get the handler for a specific link type."""
        if link_type not in self.link_registry:
            available_types = list(self.link_registry.keys())
            raise ValueError(f"No handler registered for link type: {link_type}. Available types: {available_types}")
        return self.link_registry[link_type]

    def _is_prompt_in_history(self, prompt: str) -> bool:
        """
        Check if the prompt is already in the history.
        """
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        return prompt_hash in self.prompt_history

    def _add_prompt_to_history(self, prompt: str):
        """
        Add the prompt to the history.
        """
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        self.prompt_history.append(prompt_hash)

    def _clear_prompt_history(self):
        """
        Clear the prompt history.
        """
        self.prompt_history = []

    def _populate_json_schema(self, raw_output: str, output_schema: Dict[str, Any],
                              original_prompt: str, model_name: str, temperature: float,
                              token_limit: int, execution_method: str, retry: int) -> Dict[str, Any]:
        """
        First attempt to populate the JSON Schema using the raw output.
        """
        population_prompt = f"""
Using the following JSON Schema:
{json.dumps(output_schema, indent=2)}

And the raw output below:
{raw_output}

Populate the schema accordingly and return ONLY valid JSON.
"""
        logging.info("Population prompt sent to LLM.")
        # Hash the population prompt and check if it's in history
        population_prompt_hash = hashlib.md5(population_prompt.encode('utf-8')).hexdigest()
        if population_prompt_hash in self.prompt_history:
            logging.error("Infinite loop detected! Halting execution.")
            return {"error": "Infinite loop detected"}
        self._add_prompt_to_history(population_prompt_hash)

        return self._invoke_llm(population_prompt, model_name=model_name, temperature=temperature,
                                  token_limit=token_limit, execution_method=execution_method,
                                  output_schema=output_schema, retry=retry)

    def _repair_output(self, raw_output: str, output_schema: Dict[str, Any], original_prompt: str,
                       model_name: str, temperature: float, token_limit: int, execution_method: str, retry: int) -> Dict[str, Any]:
        """
        Use a secondary LLM call to repair the output so that it exactly conforms to the JSON Schema.
        """
        repair_prompt = f"""
Your previous answer did not match the required JSON Schema.
Please repair your output so that it exactly conforms to the following JSON Schema:
{json.dumps(output_schema, indent=2)}

Ensure that the output contains valid JSON and includes ALL properties as specified.
Original raw output:
{raw_output}

Original prompt:
{original_prompt}

Return ONLY valid JSON.
"""
        logging.info("Repair prompt sent to LLM.")
        # Hash the repair prompt and check if it's in history
        repair_prompt_hash = hashlib.md5(repair_prompt.encode('utf-8')).hexdigest()
        if repair_prompt_hash in self.prompt_history:
            logging.error("Infinite loop detected! Halting execution.")
            return {"error": "Infinite loop detected"}
        self._add_prompt_to_history(repair_prompt_hash)

        return self._invoke_llm(repair_prompt, model_name=model_name, temperature=temperature,
                                  token_limit=token_limit, execution_method=execution_method,
                                  output_schema=output_schema, retry=retry)

    @lru_cache(maxsize=128)
    def _invoke_llm(self, prompt: str, model_name: str, temperature: float, token_limit: int,
                    execution_method: str, output_schema: Dict[str, Any] = None, retry: int = 1) -> Dict[str, Any]:
        """
        Common LLM invocation and JSON extraction.
        First, try to directly parse and validate the LLM's output.
        Only if that fails (and only once) do we call a population prompt.
        """
        logger.trace(f"Invoking LLM with model={model_name}, temp={temperature}, tokens={token_limit}")
        logger.trace(f"Prompt (first 200 chars): {prompt[:200]}...")
        
        # Store result struct with both raw and processed data
        result = {"raw": None, "data": {}}
        
        # Do a direct call and attempt extraction.
        llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=token_limit)
        try:
            logger.trace("Sending prompt to LLM")
            response = llm.invoke(prompt)
            raw_result = response.content  # full LLM output string
            
            # Store the raw result immediately
            result["raw"] = raw_result
            
            logger.trace(f"Received response (first 200 chars): {raw_result[:200]}...")
            logging.info(f"LLM Response: {raw_result[:200]}..." if len(raw_result) > 200 else f"LLM Response: {raw_result}")
        except Exception as e:
            logging.error(f"LLM call failed: {e}")
            logger.trace(f"LLM exception: {type(e).__name__}: {str(e)}")
            return result

        # First, check if we have a simple value response (not JSON)
        if output_schema and "properties" in output_schema and "required" in output_schema:
            # Try to handle simple responses (single number, word, etc.)
            clean_result = raw_result.strip()
            required_props = output_schema["required", []]
            
            logger.trace(f"Checking for simple response with schema: {output_schema['required']}")
            
            # Check if this might be a simple value response
            if len(required_props) == 1 and not (clean_result.startswith('{') or clean_result.startswith('[')):
                logger.trace(f"Detected potential simple value response: {clean_result}")
                try:
                    # Try to detect the type
                    prop_name = required_props[0]
                    prop_schema = output_schema["properties"].get(prop_name, {})
                    prop_type = prop_schema.get("type", "string")
                    
                    logger.trace(f"Expected property: {prop_name}, type: {prop_type}")
                    
                    # Convert to appropriate type
                    if prop_type == "integer" and clean_result.isdigit():
                        value = int(clean_result)
                        logger.trace(f"Converted to integer: {value}")
                    elif prop_type == "number" and clean_result.replace('.', '', 1).isdigit():
                        value = float(clean_result)
                        logger.trace(f"Converted to float: {value}")
                    elif prop_type == "boolean" and clean_result.lower() in ("true", "false", "yes", "no", "1", "0"):
                        value = clean_result.lower() in ("true", "yes", "1")
                        logger.trace(f"Converted to boolean: {value}")
                    else:
                        value = clean_result
                        logger.trace(f"Using as string: {value}")
                    
                    # Create a proper dictionary with the schema's required property
                    result["data"] = {prop_name: value}
                    logger.trace(f"Created structured result from simple value: {result}")
                    logging.info(f"Converted simple response to structured format: {result['data']}")
                    return result
                except Exception as e:
                    logger.trace(f"Failed to convert simple response: {e}")
                    # Continue with normal JSON extraction
        
        # Try to extract valid JSON directly.
        logger.trace("Attempting to extract and parse JSON")
        extracted = extract_json(raw_result)
        if output_schema:
            try:
                logger.trace("Attempting to parse and validate against schema")
                parsed = json.loads(extracted)
                validate(instance=parsed, schema=output_schema)
                logger.trace("JSON validation successful")
                logging.info("Direct parse: response is valid.")
                result["data"] = parsed
                return result
            except (json.JSONDecodeError, ValidationError) as e:
                logger.trace(f"JSON validation failed: {e}")
                logging.info(f"Direct parse failed: {e}")
        else:
            # No schema provided; return raw_result as a dict.
            logger.trace("No schema provided, setting raw content as data")
            result["data"] = {"raw_content": raw_result}
            return result

        # If direct parse fails and we haven't retried, call the population prompt once.
        if retry > 0:
            population_prompt = f"""
Using the following JSON Schema:
{json.dumps(output_schema, indent=2)}

And the raw output below:
{raw_result}

Populate the schema accordingly and return ONLY valid JSON.
"""
            logging.info("Population prompt sent to LLM.")
            pop_hash = hashlib.md5(population_prompt.encode('utf-8')).hexdigest()
            if pop_hash in self.prompt_history:
                logging.error("Infinite loop detected! Halting execution.")
                return {"error": "Infinite loop detected"}
            self._add_prompt_to_history(pop_hash)
            # Make a single population call.
            pop_response = self._invoke_llm(population_prompt, model_name, temperature, token_limit,
                                            execution_method, output_schema, retry-1)
            try:
                validate(instance=pop_response, schema=output_schema)
                logging.info("Population call: response validated.")
                return pop_response
            except ValidationError as ve:
                logging.error(f"Population response failed validation: {ve}")
                return {"raw_content": raw_result}
        else:
            # Final fallback: return raw output.
            return {"raw_content": raw_result}

    def _execute_user_input_link(self, link: Dict[str, Any]) -> UserInputOutput:
        logging.info(f"Prompt for user input ({link['name']}): {link.get('description', '')}")
        inputs = {}
        
        base_context = build_context(self.memory)
        
        for input_name, input_config in link['inputs'].items():
            # Process description template
            raw_description = input_config['description']
            try:
                description_template = self.env.from_string(raw_description)
                prompt_text = description_template.render(**base_context) + ": "
            except Exception as e:
                logging.error(f"Error rendering description: {e}")
                prompt_text = raw_description + ": "
            
            input_type = input_config.get('type', 'string')
            
            if input_type == 'string':
                inputs[input_name] = input(prompt_text)
                
            elif input_type == 'number':
                while True:
                    try:
                        value = input(prompt_text)
                        inputs[input_name] = float(value)
                        break
                    except ValueError:
                        print("Please enter a valid number.")
                        
            elif input_type == 'boolean':
                while True:
                    value = input(prompt_text + "(yes/no): ").lower()
                    if value in ['yes', 'y', 'true', '1']:
                        inputs[input_name] = True
                        break
                    elif value in ['no', 'n', 'false', '0']:
                        inputs[input_name] = False
                        break
                    print("Please enter 'yes' or 'no'.")
                    
            elif input_type == 'select':
                if 'options' not in input_config:
                    logging.error(f"No options provided for select input {input_name}")
                    inputs[input_name] = ""
                    continue
                    
                options = []
                # Process template in each option
                for option in input_config['options']:
                    processed_option = {'value': option['value'], 'description': option.get('description', '')}
                    
                    # Process value template
                    if isinstance(processed_option['value'], str) and '{{' in processed_option['value']:
                        try:
                            value_template = self.env.from_string(processed_option['value'])
                            processed_option['value'] = value_template.render(**base_context)
                        except Exception as e:
                            logging.error(f"Error rendering option value: {e}")
                    
                    # Process description template
                    if isinstance(processed_option['description'], str) and '{{' in processed_option['description']:
                        try:
                            desc_template = self.env.from_string(processed_option['description'])
                            processed_option['description'] = desc_template.render(**base_context)
                        except Exception as e:
                            logging.error(f"Error rendering option description: {e}")
                    
                    options.append(processed_option)
                    
                print(f"\n{prompt_text}")
                
                # Display options with numbers
                for i, option in enumerate(options, 1):
                    desc = option.get('description', '')
                    print(f"{i}. {option['value']}{' - ' + desc if desc else ''}")
                    
                # Get valid selection
                while True:
                    try:
                        selection = input("\nEnter number of your choice: ")
                        idx = int(selection) - 1
                        if 0 <= idx < len(options):
                            inputs[input_name] = options[idx]['value']
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(options)}")
                    except ValueError:
                        print("Please enter a valid number")
                        
            elif input_type == 'multiselect':
                # For selecting multiple options
                if 'options' not in input_config:
                    logging.error(f"No options provided for multiselect input {input_name}")
                    inputs[input_name] = []
                    continue
                    
                options = input_config['options']
                print(f"\n{prompt_text}")
                
                # Display options with numbers
                for i, option in enumerate(options, 1):
                    desc = option.get('description', '')
                    print(f"{i}. {option['value']}{' - ' + desc if desc else ''}")
                    
                # Get valid selections
                while True:
                    try:
                        selection = input("\nEnter numbers of your choices (comma-separated, e.g., '1,3,4'): ")
                        indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                        
                        # Validate all indices
                        if all(0 <= idx < len(options) for idx in indices):
                            inputs[input_name] = [options[idx]['value'] for idx in indices]
                            break
                        else:
                            print(f"Please enter valid numbers between 1 and {len(options)}")
                    except ValueError:
                        print("Please enter valid comma-separated numbers")
        
        # Process through LLM for validation and enhancement
        output_schema_obj = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": link['output_schema']['properties']
        }
        if "required" in link['output_schema']:
            output_schema_obj["required"] = link['output_schema']["required"]

        llm_prompt = f"""
You are a helpful assistant designed to structure user input into a JSON format that adheres to the following JSON Schema:
{json.dumps(output_schema_obj, indent=2)}

User Inputs:
{json.dumps(inputs, indent=2)}

Return ONLY valid JSON.
"""
        result = self._invoke_llm(llm_prompt, model_name="gpt-4o", temperature=0.0,
                                 token_limit=500, execution_method="direct",
                                 output_schema=output_schema_obj)
        return UserInputOutput(data=result)

    def _execute_llm_link(self, link: Dict[str, Any]) -> LLMOutput:
        logging.info(f"Prompt for LLM link ({link['name']})")
        model_name = link.get('model', "gpt-4o")
        temperature = link.get('temperature', 0.0)
        token_limit = link.get('token_limit', 512)
        execution_method = link.get('execution_method', 'direct')
        output_schema = link.get('output_schema', None)
        
        logger.trace(f"Link configuration: model={model_name}, temperature={temperature}, token_limit={token_limit}")
        
        base_context = build_context(self.memory)
        logger.trace(f"Base context keys: {list(base_context.keys())}")
        
        if "template" in link:
            try:
                template_file = link['template']['file']
                logger.trace(f"Loading template file: {template_file}")
                jinja_template = self.env.get_template(template_file)
            except TemplateError as e:
                logging.error(f"Error loading template {link['template']['file']}: {e}")
                raise e  # Re-raise the exception to stop execution
            except Exception as e:
                logging.error(f"Error loading template {link['template']['file']}: {e}")
                return LLMOutput(data={})
            
            inputs_context = {}
            if 'inputs' in link['template']:
                logger.trace(f"Processing template inputs: {list(link['template']['inputs'].keys())}")
                for key, raw_val in link['template']['inputs'].items():
                    try:
                        logger.trace(f"Rendering input '{key}': {raw_val}")
                        t = self.env.from_string(raw_val)
                        rendered_val = t.render(**base_context)
                        logger.trace(f"Rendered value: {rendered_val}")
                        inputs_context[key] = rendered_val
                    except TemplateError as e:
                        logging.error(f"Error rendering input for key '{key}': {e}")
                        raise e  # Re-raise the exception to stop execution
                    except Exception as e:
                        logging.error(f"Error rendering input for key '{key}': {e}")
                        inputs_context[key] = ""
                        
            combined_context = {**base_context, **inputs_context}
            logger.trace(f"Combined context keys: {list(combined_context.keys())}")
            try:
                logger.trace("Rendering template with combined context")
                formatted_prompt = jinja_template.render(**combined_context)
                logger.trace(f"Rendered prompt (first 200 chars): {formatted_prompt[:200]}...")
            except TemplateError as e:
                logging.error(f"Error rendering template: {e}")
                raise e  # Re-raise the exception to stop execution
            except Exception as e:
                logging.error(f"Error rendering template: {e}")
                return LLMOutput(data={})
        elif "prompt" in link:
            # Process the direct prompt string as a Jinja template
            try:
                logger.trace(f"Processing direct prompt: {link['prompt']}")
                prompt_template = self.env.from_string(link["prompt"])
                formatted_prompt = prompt_template.render(**base_context)
                logger.trace(f"Rendered prompt: {formatted_prompt}")
            except TemplateError as e:
                logging.error(f"Error rendering prompt: {e}")
                raise e  # Re-raise the exception to stop execution
            except Exception as e:
                logging.error(f"Error rendering prompt: {e}")
                return LLMOutput(data={})
        else:
            logging.error("LLM link has neither a 'template' nor a 'prompt'.")
            return LLMOutput(data={})
        
        # Check if conversation management is enabled
        conversation_mode = link.get('conversation', 'default')
        
        # Initialize conversation logs if needed
        if '__conversations' not in self.memory:
            self.memory['__conversations'] = {}
            
        if conversation_mode != 'none':
            conversation_id = conversation_mode
            logger.trace(f"Using conversation mode with ID: {conversation_id}")
            
            # Initialize this conversation if it doesn't exist
            if conversation_id not in self.memory['__conversations']:
                self.memory['__conversations'][conversation_id] = [
                    {"role": "system", "content": "You are a helpful AI assistant specializing in Eldorian language."}
                ]
                
            # Get the conversation history
            conversation = self.memory['__conversations'][conversation_id]
            
            # Add the current prompt as a user message
            conversation.append({"role": "user", "content": formatted_prompt})
            
            # Create ChatOpenAI with conversation history
            llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=token_limit)
            
            try:
                logger.trace(f"Sending conversation with {len(conversation)} messages")
                response = llm.invoke(conversation)
                raw_result = response.content
                
                # Add the response to conversation history
                conversation.append({"role": "assistant", "content": raw_result})
                # Add conversation pruning
                if len(conversation) > MAX_CONVERSATION_LENGTH:
                    # Keep system prompt + most recent messages
                    conversation = conversation[:1] + conversation[-(MAX_CONVERSATION_LENGTH-1):]
                    logger.trace(f"Pruned conversation history to {len(conversation)} messages")
                
                # Process the result as usual
                result = {"raw": raw_result}
                
                # Process with schema if available
                if output_schema:
                    try:
                        logger.trace("Attempting to parse and validate against schema")
                        extracted = extract_json(raw_result)
                        parsed = json.loads(extracted)
                        validate(instance=parsed, schema=output_schema)
                        logger.trace("JSON validation successful")
                        result["data"] = parsed
                    except (json.JSONDecodeError, ValidationError) as e:
                        logger.trace(f"Schema validation failed, processing with schema handler: {e}")
                        # Use schema processor for structured extraction
                        result["data"] = self._process_output_schema(raw_result, output_schema, build_context(self.memory))
                else:
                    # No schema, use raw content
                    result["data"] = {"raw_content": raw_result}
                    
                return LLMOutput(raw=result.get("raw"), data=result.get("data", {}))
                
            except Exception as e:
                logging.error(f"Error in conversation mode: {e}")
                return LLMOutput(raw=f"Error: {str(e)}", data={"error": str(e)})
        else:
            # Non-conversation mode, use existing implementation
            result = self._invoke_llm(formatted_prompt, model_name=model_name, temperature=temperature,
                                     token_limit=token_limit, execution_method=execution_method,
                                     output_schema=output_schema)
            return LLMOutput(raw=result.get("raw"), data=result.get("data", {}))

    def _function_random_number(self, min_value=1, max_value=3):
        """Generate a random integer between min_value and max_value."""
        return {"num_events": random.randint(min_value, max_value)}
    
    def _function_syllable_generator(self, language_style="Generic"):
        """Generate random syllables based on language style."""
        syllables = {
            "Old Elven": ["thae", "syl", "dri", "gal", "fea", "ara", "el"],
            "Modern Elven": ["luv", "fal", "sev", "fleur", "lune", "lend"],
            "Old Dwarven": ["thrang", "drom", "var", "grim", "hrot", "hal"],
            "Sylvan": ["kro", "gly", "vich", "gry", "dru", "bran", "zvil"],
            "Celestial": ["ral", "esa", "onth", "rav", "liar", "ain", "doth"],
            "Draconic": ["zalt", "krum", "krox", "mach", "dorf", "stur"]
        }
        style = language_style if language_style in syllables else "Generic"
        if style == "Generic":
            return {"syllable": "ka"}
        return {"syllable": random.choice(syllables[style])}
        
    def _function_terminate_process(self, condition=False, message="Process terminated by request"):
        """
        Terminates the process if the condition is truthy.
        
        Args:
            condition: If truthy, the process will terminate
            message: Optional message to log when terminating
            
        Returns:
            Dict with termination status information
        """
        if condition:
            logging.warning(f"Terminating process: {message}")
            raise TerminateProcessException(message)
        
        return {
            "terminated": False,
            "message": "Process continues"
        }
    
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
                    # Keep existing JS execution path
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
                
                if function_name in self.function_registry:
                    try:
                        result = self.function_registry[function_name](**inputs)
                        logging.info(f"Registry function result: {result}")
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
        logger.trace(f"Base context keys: {list(base_context.keys())}")
        
        for key, input_config in link["inputs"].items():
            logger.trace(f"Processing input '{key}': {input_config}")
            
            # Handle different input configurations
            if isinstance(input_config, dict):
                # Static configuration with possible default
                if "value" in input_config:
                    logger.trace(f"Using static value for '{key}': {input_config['value']}")
                    inputs[key] = input_config["value"]
                elif "default" in input_config:
                    logger.trace(f"Using default value for '{key}': {input_config['default']}")
                    inputs[key] = input_config["default"]
                else:
                    logger.trace(f"No value or default for '{key}', setting to None")
                    inputs[key] = None
            elif isinstance(input_config, str) and "{{" in input_config and "}}" in input_config:
                # It's a Jinja template reference
                try:
                    logger.trace(f"Rendering template reference for '{key}': {input_config}")
                    t = self.env.from_string(input_config)
                    rendered_val = t.render(**base_context)
                    logger.trace(f"Rendered value: '{rendered_val}'")
                    
                    # Try to convert to appropriate type
                    try:
                        # Try as number first
                        if rendered_val.isdigit():
                            inputs[key] = int(rendered_val)
                            logger.trace(f"Converted '{key}' to integer: {inputs[key]}")
                        elif rendered_val.replace('.', '', 1).isdigit():
                            inputs[key] = float(rendered_val)
                            logger.trace(f"Converted '{key}' to float: {inputs[key]}")
                        else:
                            inputs[key] = rendered_val
                            logger.trace(f"Using '{key}' as string: {inputs[key]}")
                    except Exception as e:
                        logger.trace(f"Type conversion failed for '{key}': {e}")
                        inputs[key] = rendered_val
                except Exception as e:
                    logging.error(f"Error rendering input for key '{key}': {e}")
                    inputs[key] = None
            else:
                # Direct static value
                logger.trace(f"Using direct value for '{key}': {input_config}")
                inputs[key] = input_config
        
        logger.trace(f"Processed function inputs: {inputs}")
        return inputs

    def execute_recipe(self):
        logger.trace("Starting recipe execution")
        self._clear_prompt_history()  # Clear prompt history at the start of each recipe execution
        try:
            for link in self.links:
                link_name = link['name']
                link_type = link['type']
                
                logger.trace(f"Processing link: {link_name} (type: {link_type})")
                
                # Check if link has a condition
                if 'condition' in link:
                    try:
                        logger.trace(f"Evaluating condition for link {link_name}: {link['condition']}")
                        # Evaluate the condition using Jinja2 template
                        base_context = build_context(self.memory)
                        condition_template = self.env.from_string(link['condition'])
                        condition_result = condition_template.render(**base_context)
                        logger.trace(f"Condition result: '{condition_result}'")
                        
                        # Convert string result to boolean
                        condition_met = False
                        if condition_result.lower() in ('true', 'yes', '1'):
                            condition_met = True
                        elif condition_result.isdigit() and int(condition_result) > 0:
                            condition_met = True
                        
                        logger.trace(f"Condition evaluated to: {condition_met}")
                        if not condition_met:
                            logging.info(f"Skipping link '{link_name}' because condition was not met")
                            continue
                    except Exception as e:
                        logging.error(f"Error evaluating condition for link '{link_name}': {e}")
                        logger.trace(f"Condition evaluation exception: {type(e).__name__}: {str(e)}")
                        # Default to executing the link if condition evaluation fails
                
                logging.info(f"Executing link: {link_name}")
                
                try:
                    # Use the registry pattern instead of if/else chain
                    handler = self.get_link_handler(link_type)
                    logger.trace(f"Got handler for {link_type}: {handler.__class__.__name__}")
                    
                    output = handler.execute(link, self.memory)
                    logger.trace(f"Handler execution completed with raw output: {output.raw is not None}")
                    
                    key = link_name.replace(" ", "_")
                    self.memory[key] = output
                    logger.trace(f"Stored output in memory with key: {key}")
                    logging.info(f"Output for {key}: {output.data if output.data else 'See raw output'}")
                except TerminateProcessException as e:
                    logging.warning(f"Recipe execution terminated: {e.message}")
                    logger.trace(f"Termination reason: {e.message}")
                    return
                except ValueError as e:
                    logging.error(f"Error executing link {link_name}: {e}")
                    logger.trace(f"ValueError during execution: {str(e)}")
                    # Could continue with next link or raise based on preference
                    
            logger.trace("Recipe execution completed successfully")
        except Exception as e:
            logging.error(f"Error executing recipe: {e}")
            logger.trace(f"Exception during recipe execution: {type(e).__name__}: {str(e)}")
            raise

    def format_template_with_params(self, template: str, params: Dict[str, Any]) -> str:
        """
        More advanced template formatting with detailed logging and better error handling.
        Supports both {{param}} and {param} formats.
        
        Args:
            template: Template string with placeholders
            params: Dictionary of parameter values
            
        Returns:
            Formatted template string with parameters substituted
        """
        logger.trace(f"Formatting template with params: {params}")
        result = template
        
        # First, handle double-brace format {{param}}
        double_brace_pattern = re.compile(r'\{\{([^{}]+)\}\}')
        placeholders = double_brace_pattern.findall(template)
        
        # Check that all required parameters are present
        missing = [p for p in placeholders if p not in params]
        if missing:
            logger.warning(f"Missing required template parameters: {missing}")
            # Continue with empty values rather than failing
        
        # Replace each placeholder
        for placeholder in placeholders:
            if placeholder in params:
                value = str(params.get(placeholder, ""))
                logger.trace(f"Replacing placeholder '{{{{'{placeholder}'}}}}' with: {value}")
                result = result.replace("{{" + placeholder + "}}", value)
            else:
                logger.trace(f"Placeholder '{{{{'{placeholder}'}}}}' not found in params, leaving as is")
                
        # Also handle single-brace format {param} for backward compatibility
        single_brace_pattern = re.compile(r'\{([^{}]+)\}')
        single_placeholders = single_brace_pattern.findall(result)
        
        for placeholder in single_placeholders:
            if placeholder in params:
                value = str(params.get(placeholder, ""))
                logger.trace(f"Replacing single-brace placeholder {{{placeholder}}} with: {value}")
                result = result.replace("{" + placeholder + "}", value)
        
        logger.trace(f"Final formatted template: {result[:200]}...")
        return result

    def _process_output_schema(self, raw_output: str, schema: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw LLM output into a structured format that conforms to the provided schema.
        Uses a specialized prompt to extract structured data from the raw output.
        
        Args:
            raw_output: Raw text from LLM response
            schema: JSON schema defining the expected structure
            context: Current execution context
            
        Returns:
            Structured data conforming to the schema
        """
        logger.trace(f"Processing output schema")
        logger.trace(f"Schema: {schema}")
        logger.trace(f"Raw output (first 200 chars): {raw_output[:200]}...")
        
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Structured Data",
            "description": "Data extracted from the raw output",
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
        logger.trace(f"Conversion prompt created")
        
        try:
            # Use a more constrained model for structured data extraction
            result = self._invoke_llm(
                prompt=conversion_prompt,
                model_name="gpt-4o",
                temperature=0.0,  # Zero temperature for deterministic outputs
                token_limit=1000,
                execution_method="direct",
                output_schema=json_schema,
                retry=0  # No retry for schema processing to avoid loops
            )
            
            # Extract the data portion of the result
            if isinstance(result, dict) and "data" in result:
                structured_data = result["data"]
            else:
                structured_data = result
                
            logger.trace(f"Structured data extracted: {structured_data}")
            return structured_data
        except Exception as e:
            logger.error(f"Error during schema processing: {e}")
            # Return empty dict on failure rather than raising exception
            return {}

class LexiconEntry:
    def __init__(self, word_data, schema_version="1.0"):
        self.data = word_data
        self.metadata = {
            "schema_version": schema_version,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "recipe_id": word_data.get("recipe_id", "eldorian_word_v1")
        }
    
    def to_dict(self):
        return {
            "data": self.data,
            "metadata": self.metadata
        }

class LexiconIndex:
    def __init__(self):
        self.by_eldorian = {}
        self.by_english = {}
        self.by_origin_language = {}
        self.by_semantic_field = {}
        self.by_phonetic_pattern = {}
        
    def add_word(self, word_entry):
        # Index by Eldorian word
        self.by_eldorian[word_entry["eldorian"]] = word_entry["word_id"]
        
        # Index by English meaning
        english = word_entry["english"]
        if english not in self.by_english:
            self.by_english[english] = []
        self.by_english[english].append(word_entry["word_id"])
        
        # Index by origin language
        for origin in word_entry.get("etymology", {}).get("origin_words", []):
            lang = origin.get("origin_language")
            if lang:
                if lang not in self.by_origin_language:
                    self.by_origin_language[lang] = []
                self.by_origin_language[lang].append(word_entry["word_id"])



def find_words_by_criteria(criteria, lexicon_dir="lexicon"):
    """
    Find words matching specific criteria.
    
    Example criteria:
    {
        "english_contains": "beauty",
        "origin_language": "Old Elven",
        "part_of_speech": "adjective"
    }
    """
    results = []
    candidates = []
    
    
    # Load appropriate indices based on criteria
    if "english_contains" in criteria:
        with open(f"{lexicon_dir}/indices/by_english.json") as f:
            english_index = json.load(f)
        
        # Find potential matches
        for eng, word_ids in english_index.items():
            if criteria["english_contains"].lower() in eng.lower():
                candidates.extend(word_ids)
    
    # Apply additional filters
    final_results = []
    for word_id in candidates:
        word_path = f"{lexicon_dir}/words/{word_id}.json"
        if not os.path.exists(word_path):
            logging.warning(f"Word file {word_path} does not exist")
            continue
            
        try:
            with open(word_path) as f:
                word = json.load(f)
            
            # Continue with your criteria checking...
            if "origin_language" in criteria:
                # Use safer nested attribute access with get()
                origin_words = word.get("recipe_output", {}).get("Generate_the_Origin_Words", {}).get("data", {}).get("origin_words", [])
                if any(origin.get("origin_language") == criteria["origin_language"] for origin in origin_words):
                    final_results.append(word)
        except Exception as e:
            logging.error(f"Error loading word file {word_path}: {e}")
    
    return final_results

def process_recipe_to_word_entry(recipe_output):
    """Transform recipe output to standardized word entry conforming to the schema."""
    # Extract base information from recipe output
    apply_phonology = recipe_output.get("Apply_Phonology")
    initial_inputs = recipe_output.get("Initial_User_Inputs")
    
    # Safely extract data with proper fallbacks
    phonology_data = apply_phonology.get_data(fallback_to_raw=True) if hasattr(apply_phonology, 'get_data') else {}
    input_data = initial_inputs.get_data(fallback_to_raw=True) if hasattr(initial_inputs, 'get_data') else {}
    
    # Basic word properties
    eldorian_word = phonology_data.get("updated_word", "unknown")
    english_word = input_data.get("english_word", "unknown")
    part_of_speech = input_data.get("part_of_speech", "unknown")
    
    # Generate a consistent ID
    word_id = f"{eldorian_word.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}"
    
    # Extract etymological data
    origin_data = {}
    if "Generate_the_Origin_Words" in recipe_output:
        origin_link = recipe_output["Generate_the_Origin_Words"]
        if hasattr(origin_link, 'get_data'):
            origin_data = origin_link.get_data(fallback_to_raw=True)
    
    origin_words = origin_data.get("origin_words", [])
    
    # Extract pronunciation
    pronunciation = {}
    if "Pronunciation" in recipe_output:
        pron_link = recipe_output["Pronunciation"]
        if hasattr(pron_link, 'get_data'):
            pron_data = pron_link.get_data(fallback_to_raw=True)
            pronunciation = {
                "ipa": pron_data.get("ipa", ""),
                "stress_pattern": pron_data.get("stress_pattern", "")
            }
    
    # Create appropriate grammatical properties based on part of speech
    grammatical_properties = create_grammatical_properties(part_of_speech, recipe_output)
    
    # Build the complete word entry
    word_entry = {
        "word_id": word_id,
        "eldorian": eldorian_word,
        "english": english_word,
        "core": {
            "part_of_speech": part_of_speech,
            "pronunciation": pronunciation,
            "syllables": phonology_data.get("syllables", []),
            "connotation": origin_data.get("revised_connotation", ""),
            "definitions": [
                {
                    "meaning": english_word,
                    "domain": origin_data.get("semantic_domain", "general"),
                    "register": origin_data.get("register", "standard"),
                    "examples": []
                }
            ]
        },
        "grammatical_properties": grammatical_properties,
        "etymology": {
            "origin_words": [
                {
                    "word": origin.get("word", ""),
                    "language": origin.get("language", ""),
                    "meaning": origin.get("meaning", "")
                }
                for origin in origin_words
            ]
        },
        "relationships": {
            "derivatives": [],
            "synonyms": [],
            "antonyms": [],
            "morphological": [],
            "semantic": [],
            "etymological": []
        },
        "homonyms": [],
        "metadata": {
            "schema_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "recipe_id": "eldorian_word_v1",
            "tags": []
        },
        "generation_data": {
            "processed_output": {},
            "raw_output": {}
        }
    }
    
    # Store generation data for reference
    for step_name, step_output in recipe_output.items():
        if hasattr(step_output, 'data'):
            word_entry["generation_data"]["processed_output"][step_name] = step_output.data
        if hasattr(step_output, 'raw'):
            word_entry["generation_data"]["raw_output"][step_name] = step_output.raw
    
    return word_entry

def create_grammatical_properties(part_of_speech, recipe_output):
    """Create appropriate grammatical properties based on part of speech."""
    if part_of_speech == "noun":
        return {
            "$type": "NounProperties",
            "gender": "neutral",  # Default value
            "countability": "countable",  # Default value
            "declension_class": "regular",  # Default value
            "case_forms": {
                "nominative": {
                    "singular": recipe_output.get("Apply_Phonology", {}).get_data().get("updated_word", ""),
                    "plural": ""  # To be filled later
                }
            }
        }
    elif part_of_speech == "verb":
        return {
            "$type": "VerbProperties",
            "transitivity": "intransitive",  # Default value
            "conjugation_class": "regular",  # Default value
            "tense_forms": {
                "present": {
                    "first_singular": recipe_output.get("Apply_Phonology", {}).get_data().get("updated_word", ""),
                    "second_singular": "",
                    "third_singular": "",
                    "first_plural": "",
                    "second_plural": "",
                    "third_plural": ""
                }
            },
            "infinitive": ""  # To be filled later
        }
    elif part_of_speech == "adjective":
        return {
            "$type": "AdjectiveProperties",
            "comparison": {
                "comparative": "",
                "superlative": ""
            },
            "agreement_forms": {
                "masculine": "",
                "feminine": "",
                "neuter": recipe_output.get("Apply_Phonology", {}).get_data().get("updated_word", ""),
                "plural": ""
            }
        }
    else:
        return {
            "$type": "OtherProperties",
            "variations": {}
        }
def migrate_word_to_schema_version(word_entry, target_version):
    """Migrate a word entry to a newer schema version."""
    current_version = word_entry.get("metadata", {}).get("schema_version", "1.0")
    
    if current_version == target_version:
        return word_entry
    
    # Version upgrade paths
    if current_version == "1.0" and target_version == "1.1":
        # Example migration: Add new required field
        if "usage_examples" not in word_entry:
            word_entry["usage_examples"] = []
        
        # Update version
        word_entry["metadata"]["schema_version"] = "1.1"
        word_entry["metadata"]["updated_at"] = datetime.now().isoformat()
    
    return word_entry

def update_lexicon_indices(word_entry, lexicon_dir="lexicon"):
    """Update lexicon indices with new word entry."""
    # Create directory if it doesn't exist
    indices_dir = f"{lexicon_dir}/indices"
    os.makedirs(indices_dir, exist_ok=True)
    
    # Load existing indices or create new ones
    english_index_path = f"{indices_dir}/by_english.json"
    if os.path.exists(english_index_path):
        with open(english_index_path) as f:
            english_index = json.load(f)
    else:
        english_index = {}
    
    # Update English index
    english = word_entry.get("english", "").lower()
    if english:
        if english not in english_index:
            english_index[english] = []
        english_index[english].append(word_entry["word_id"])
    
    # Save updated index
    with open(english_index_path, 'w') as f:
        json.dump(english_index, f, indent=2)

def repair_word_entry(word_entry, schema):
    """Attempt to repair a word entry that failed schema validation."""
    # Add missing required fields with defaults
    for prop in schema.get("required", []):
        if prop not in word_entry:
            word_entry[prop] = None
            
    # If core properties are required but missing
    if "core" in schema.get("required", []) and "core" not in word_entry:
        word_entry["core"] = {}
        
    # Add other missing required fields
    if "metadata" not in word_entry:
        word_entry["metadata"] = {
            "schema_version": "1.0",
            "created_at": datetime.now().isoformat()
        }
        
    logging.info(f"Repaired word entry to conform to schema")
    return word_entry

if __name__ == '__main__':
    recipe_path = 'recipes/eldorian_word.yaml'
    recipe = EldorianWordRecipe(recipe_path)
    recipe.execute_recipe()