"""
Plugin discovery and loading system.
"""
import os
import json
import importlib
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Registry of loaded plugins
_loaded_plugins = {}

def discover_plugins() -> List[str]:
    """
    Discover available plugins in the plugins directory.
    
    Returns:
        List of plugin names
    """
    plugins_dir = os.path.dirname(os.path.abspath(__file__))
    plugins = []
    
    for item in os.listdir(plugins_dir):
        plugin_path = os.path.join(plugins_dir, item)
        if os.path.isdir(plugin_path) and not item.startswith("__"):
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if os.path.exists(manifest_path):
                plugins.append(item)
    
    return plugins

def load_plugin(plugin_name: str) -> Optional[Dict[str, Any]]:
    """
    Load a plugin by name.
    
    Args:
        plugin_name: The name of the plugin to load
        
    Returns:
        Plugin manifest data if loaded successfully, None otherwise
    """
    if plugin_name in _loaded_plugins:
        return _loaded_plugins[plugin_name]
        
    plugins_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_path = os.path.join(plugins_dir, plugin_name)
    manifest_path = os.path.join(plugin_path, "manifest.json")
    
    if not os.path.exists(manifest_path):
        logger.error(f"Plugin '{plugin_name}' does not have a manifest.json file")
        return None
        
    try:
        # Load the manifest
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        # Import the plugin module
        plugin_module = importlib.import_module(f"plugins.{plugin_name}")
        
        # Register the plugin
        _loaded_plugins[plugin_name] = manifest
        
        # Process entry points
        if "entry_points" in manifest:
            # Process link handlers
            if "link_handlers" in manifest["entry_points"]:
                for handler_file in manifest["entry_points"]["link_handlers"]:
                    try:
                        importlib.import_module(f"plugins.{plugin_name}.{handler_file.replace('.py', '')}")
                    except ImportError as e:
                        logger.error(f"Failed to load link handler {handler_file} for plugin {plugin_name}: {e}")
        
        return manifest
    except Exception as e:
        logger.error(f"Failed to load plugin '{plugin_name}': {e}")
        return None

def load_all_plugins() -> Dict[str, Dict[str, Any]]:
    """
    Discover and load all available plugins.
    
    Returns:
        Dictionary mapping plugin names to their manifest data
    """
    plugins = discover_plugins()
    for plugin_name in plugins:
        load_plugin(plugin_name)
    return _loaded_plugins

def get_plugin_info(plugin_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a loaded plugin.
    
    Args:
        plugin_name: The name of the plugin
        
    Returns:
        Plugin manifest data if loaded, None otherwise
    """
    return _loaded_plugins.get(plugin_name)

# Load all plugins when this module is loaded
load_all_plugins()
