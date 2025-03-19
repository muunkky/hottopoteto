"""
Utility functions for storage domain
"""
import os
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

def ensure_directory(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False
        
def safe_load_json(file_path: str, default: Any = None) -> Any:
    """
    Safely load a JSON file, returning a default value if loading fails.
    """
    if not os.path.exists(file_path):
        return default if default is not None else {}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return default if default is not None else {}
        
def safe_save_json(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Safely save data to a JSON file.
    """
    try:
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory(directory)
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False
