# This file makes the directory a Python package
"""
Core utility functions for the LangChain v2 system.
"""
import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

def ensure_directory(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False on error
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False

def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID, optionally with a prefix.
    
    Args:
        prefix: Optional prefix to add to the ID
        
    Returns:
        Generated ID string
    """
    unique_id = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix.lower()}-{unique_id}"
    return unique_id

def safe_load_json(file_path: str, default: Any = None) -> Any:
    """
    Safely load a JSON file, returning a default value if loading fails.
    
    Args:
        file_path: Path to the JSON file
        default: Default value to return on failure (default: None)
        
    Returns:
        Loaded JSON data or default value
    """
    if default is None:
        default = {}
        
    if not os.path.exists(file_path):
        return default
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return default
        
def safe_save_json(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Safely save data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        indent: Indentation level (default: 2)
        
    Returns:
        True if save succeeded, False otherwise
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory(directory)
            
        # Save the file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False
        
def format_timestamp(timestamp: Optional[Union[str, datetime]] = None) -> str:
    """
    Format a timestamp for consistent use throughout the system.
    
    Args:
        timestamp: Timestamp to format (default: current time)
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
        
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    
    return timestamp.isoformat()
