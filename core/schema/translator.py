"""
Schema translation utilities using LLM assistance
"""
import json
import logging
from typing import Dict, Any, Optional, List, Union
from langchain_openai import ChatOpenAI
from jsonschema import validate, ValidationError
from core.security.credentials import get_credential

logger = logging.getLogger(__name__)

def is_valid_for_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Check if data conforms to a JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema
        
    Returns:
        True if valid, False otherwise
    """
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False

def adapt_data_to_schema(data: Dict[str, Any], target_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use LLM to adapt data from one format to another based on target schema.
    
    Args:
        data: Source data that doesn't conform to schema
        target_schema: Schema that the data should conform to
        
    Returns:
        Transformed data conforming to target schema
    """
    if is_valid_for_schema(data, target_schema):
        # Data already conforms to schema
        return data
    
    # Create a prompt for the LLM to transform the data
    prompt = f"""
    Transform the following JSON data to match the target schema.
    Only include fields that are in the target schema.
    Make intelligent decisions about mapping fields and values.
    
    Input Data:
    {json.dumps(data, indent=2)}
    
    Target Schema:
    {json.dumps(target_schema, indent=2)}
    
    Transformed JSON data (valid according to the schema):
    """
    
    # Use ChatGPT to transform the data
    try:
        api_key = get_credential("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0.0)
        response = llm.invoke(prompt)
        
        # Extract and parse JSON
        start_idx = response.content.find('{')
        end_idx = response.content.rfind('}')
        
        if start_idx >= 0 and end_idx >= 0:
            json_str = response.content[start_idx:end_idx+1]
            transformed_data = json.loads(json_str)
            
            # Verify the transformed data is valid
            if is_valid_for_schema(transformed_data, target_schema):
                return transformed_data
            else:
                logger.warning("LLM transformed data but it still doesn't match schema")
                # Try one more time with more explicit instructions
                return retry_adaptation(data, transformed_data, target_schema)
    except Exception as e:
        logger.error(f"Error adapting data to schema: {e}")
    
    # If all else fails, return a best-effort filtered dictionary
    return {k: v for k, v in data.items() if k in target_schema.get("properties", {}).keys()}

def retry_adaptation(original_data: Dict[str, Any], 
                    first_attempt: Dict[str, Any], 
                    target_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a second attempt at adapting data to schema with more explicit instructions.
    
    Args:
        original_data: Original source data
        first_attempt: First attempt at transformation
        target_schema: Target schema
        
    Returns:
        Improved transformation
    """
    # Find validation errors in first attempt
    errors = []
    try:
        validate(instance=first_attempt, schema=target_schema)
    except ValidationError as e:
        errors = [err.message for err in e.context]
    
    error_text = "\n".join([f"- {err}" for err in errors]) if errors else "The data doesn't match the schema."
    
    prompt = f"""
    The transformed data still doesn't match the target schema.
    
    Original Data:
    {json.dumps(original_data, indent=2)}
    
    First Attempt:
    {json.dumps(first_attempt, indent=2)}
    
    Target Schema:
    {json.dumps(target_schema, indent=2)}
    
    Validation Errors:
    {error_text}
    
    Please carefully correct the data to match the schema exactly.
    Only return valid JSON that matches the schema.
    """
    
    try:
        api_key = get_credential("OPENAI_API_KEY")
        llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0.0)
        response = llm.invoke(prompt)
        
        # Extract and parse JSON
        start_idx = response.content.find('{')
        end_idx = response.content.rfind('}')
        
        if start_idx >= 0 and end_idx >= 0:
            json_str = response.content[start_idx:end_idx+1]
            transformed_data = json.loads(json_str)
            return transformed_data
    except Exception as e:
        logger.error(f"Error in retry adaptation: {e}")
    
    # Last resort: create a minimal valid object from the schema
    return create_minimal_valid_object(target_schema)

def create_minimal_valid_object(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a minimal valid object based on a schema.
    
    Args:
        schema: JSON schema
        
    Returns:
        Minimal valid object
    """
    result = {}
    
    # Add required properties with minimal valid values
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if "required" in schema and prop_name in schema["required"]:
                result[prop_name] = get_default_for_type(prop_schema)
    
    return result

def get_default_for_type(schema: Dict[str, Any]) -> Any:
    """
    Get a default value for a schema type.
    
    Args:
        schema: JSON schema for a property
        
    Returns:
        Default value
    """
    schema_type = schema.get("type")
    
    if schema_type == "string":
        return schema.get("default", "")
    elif schema_type == "number":
        return schema.get("default", 0)
    elif schema_type == "integer":
        return schema.get("default", 0)
    elif schema_type == "boolean":
        return schema.get("default", False)
    elif schema_type == "array":
        return schema.get("default", [])
    elif schema_type == "object":
        return schema.get("default", {})
    elif schema_type is None:
        return None
    else:
        return None
