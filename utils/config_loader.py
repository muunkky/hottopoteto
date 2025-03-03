# utils/config_loader.py
import os
import re
import yaml
import logging
from models import Recipe  # Assuming models.py is in the root directory
from pydantic import BaseModel, ValidationError

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StepConfig(BaseModel):
    name: str
    type: str
    template: str = None
    query: str = None
    function: str = None
    parameters: dict = {}
    output_format: str
    token_limit: int = None
    db_config: str = None

def substitute_env_vars(obj):
    """
    Recursively substitute environment variable placeholders in the provided object.
    
    Placeholders should be in the format: ${VAR_NAME}
    """
    if isinstance(obj, dict):
        return {k: substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        pattern = re.compile(r"\$\{([^}^{]+)\}")
        matches = pattern.findall(obj)
        for match in matches:
            env_value = os.environ.get(match)
            if env_value is not None:
                obj = obj.replace("${" + match + "}", env_value)
            else:
                logger.warning(f"Environment variable '{match}' not set. Leaving placeholder as-is.")
        return obj
    else:
        return obj

def load_config(filepath: str) -> Recipe:
    """
    Load a YAML configuration file, substitute environment variables,
    and return its content as a validated Recipe model.
    
    Args:
        filepath (str): Path to the YAML file.
    
    Returns:
        Recipe: Validated configuration data as a Recipe model.
    """
    try:
        with open(filepath, "r") as file:
            data = yaml.safe_load(file)
        logger.info(f"Successfully loaded configuration file: {filepath}")
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {filepath}")
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in file {filepath}: {e}")
        raise Exception(f"Error parsing YAML file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while reading {filepath}: {e}")
        raise Exception(f"Error reading configuration file: {e}")
    
    # Substitute environment variables in the loaded data
    data = substitute_env_vars(data)
    
    # Validate the configuration against our Recipe model
    try:
        recipe = Recipe(**data)
        logger.info("Configuration validation successful.")
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise ValueError(f"Configuration validation error: {e}")
    
    return recipe

def load_recipe(path):
    with open(path, "r") as file:
        data = yaml.safe_load(file)
    try:
        return [StepConfig(**step) for step in data["steps"]]
    except ValidationError as e:
        raise ValueError(f"Invalid Recipe: {e}")
