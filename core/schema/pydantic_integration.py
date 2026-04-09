"""
Utilities to integrate Pydantic models with recipes
"""
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import yaml

def generate_recipe_template(
    link_type: str, 
    input_model: Type[BaseModel] = None, 
    output_model: Type[BaseModel] = None,
    description: str = ""
) -> str:
    """
    Generate a recipe template YAML from Pydantic models.
    
    Args:
        link_type: The type of link to create
        input_model: Optional Pydantic model for link inputs
        output_model: Optional Pydantic model for expected outputs
        description: Description for the generated link
        
    Returns:
        YAML string for the recipe template
    """
    link_template = {
        "name": f"{link_type.replace('.', '_')}_Link",
        "type": link_type,
        "description": description
    }
    
    # Add input fields from model
    if input_model:
        inputs = {}
        for field_name, field in input_model.__annotations__.items():
            if field_name not in input_model.model_fields:
                continue
            field_info = input_model.model_fields[field_name]
            field_def = {
                "type": _get_field_type(field),
                "description": field_info.description or f"{field_name} input"
            }

            # Add required flag if field is required (Pydantic v2 API)
            if field_info.is_required():
                field_def["required"] = True

            # Add default if available and not the required sentinel
            default = field_info.default
            if not field_info.is_required() and default is not None:
                from pydantic_core import PydanticUndefinedType
                if not isinstance(default, PydanticUndefinedType):
                    field_def["default"] = default

            inputs[field_name] = field_def
            
        link_template["inputs"] = inputs
    
    # Add output schema from model
    if output_model:
        link_template["output_schema"] = output_model.model_json_schema()
    
    return yaml.dump({"links": [link_template]}, sort_keys=False)

def _get_field_type(field) -> str:
    """Convert Pydantic field type to JSON schema type"""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }
    
    # Handle simple types
    for py_type, schema_type in type_map.items():
        if field is py_type:
            return schema_type
            
    # Handle typing types (List, Dict, etc.)
    origin = getattr(field, "__origin__", None)
    if origin:
        for py_type, schema_type in type_map.items():
            if origin is py_type:
                return schema_type
    
    # Default to string if we can't determine
    return "string"
