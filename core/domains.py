"""Domain interface registry and utilities."""
from typing import Dict, Any, List, Set, Type, Optional
import os
import json
import importlib
import logging

logger = logging.getLogger(__name__)

# Registry of domain interfaces and utilities
_domain_interfaces = {}
_domain_packages = {}

def register_domain_interface(domain_name: str, interface_data: Dict[str, Any]) -> None:
    """Register a domain interface with standard schemas and utilities."""
    _domain_interfaces[domain_name] = interface_data
    if domain_name not in _domain_packages:
        _domain_packages[domain_name] = set()

def register_package_for_domain(domain_name: str, package_name: str) -> None:
    """Register a package as supporting a specific domain."""
    if domain_name not in _domain_interfaces:
        # Auto-create the domain interface if it doesn't exist
        register_domain_interface(domain_name, {
            "name": domain_name,
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        })
    
    if domain_name not in _domain_packages:
        _domain_packages[domain_name] = set()
    _domain_packages[domain_name].add(package_name)

def get_packages_for_domain(domain_name: str) -> Set[str]:
    """Get all packages that support a specific domain."""
    return _domain_packages.get(domain_name, set())

def get_domain_interface(domain_name: str) -> Optional[Dict[str, Any]]:
    """Get the interface definition for a domain."""
    return _domain_interfaces.get(domain_name)

def list_domains() -> List[str]:
    """List all registered domains."""
    return list(_domain_interfaces.keys())

def register_domain_schema(domain_name: str, schema_name: str, schema: Dict[str, Any]) -> None:
    """Register a schema for a domain."""
    if domain_name not in _domain_interfaces:
        register_domain_interface(domain_name, {
            "name": domain_name,
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        })
    
    # First, register with the central schema registry
    from core.schemas import register_schema
    register_schema(f"{domain_name}.{schema_name}", schema)
    
    # Then add to the domain interface
    schema_info = {
        "name": schema_name,
        "schema": schema
    }
    
    # Check if schema already exists
    existing_schemas = _domain_interfaces[domain_name].get("schemas", [])
    for idx, existing in enumerate(existing_schemas):
        if existing.get("name") == schema_name:
            existing_schemas[idx] = schema_info
            break
    else:
        # Schema doesn't exist, append it
        if "schemas" not in _domain_interfaces[domain_name]:
            _domain_interfaces[domain_name]["schemas"] = []
        _domain_interfaces[domain_name]["schemas"].append(schema_info)

def register_domain_function(domain_name: str, function_name: str, function_handler: Any) -> None:
    """Register a function for a domain."""
    if domain_name not in _domain_interfaces:
        register_domain_interface(domain_name, {
            "name": domain_name,
            "version": "1.0.0", 
            "schemas": [],
            "functions": []
        })
    
    function_info = {
        "name": function_name,
        "function": function_handler
    }
    
    # Check if function already exists
    existing_functions = _domain_interfaces[domain_name].get("functions", [])
    for idx, existing in enumerate(existing_functions):
        if existing.get("name") == function_name:
            existing_functions[idx] = function_info
            break
    else:
        # Function doesn't exist, append it
        if "functions" not in _domain_interfaces[domain_name]:
            _domain_interfaces[domain_name]["functions"] = []
        _domain_interfaces[domain_name]["functions"].append(function_info)

def get_domain_function(domain_name: str, function_name: str) -> Optional[Any]:
    """Get a function registered for a domain."""
    domain_interface = _domain_interfaces.get(domain_name)
    if not domain_interface:
        return None
        
    functions = domain_interface.get("functions", [])
    for func in functions:
        if func.get("name") == function_name:
            return func.get("function")
    
    return None

def discover_domains() -> None:
    """
    Discover domains from both built-in and plugin sources.
    """
    # First, load built-in domains
    domains_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "domains")
    if os.path.exists(domains_dir):
        for item in os.listdir(domains_dir):
            domain_path = os.path.join(domains_dir, item)
            if os.path.isdir(domain_path) and not item.startswith("__"):
                try:
                    importlib.import_module(f"domains.{item}")
                    logger.info(f"Loaded built-in domain: {item}")
                except ImportError as e:
                    logger.error(f"Failed to load built-in domain '{item}': {e}")
    
    # Then, discover domains from plugins
    try:
        from plugins import get_plugin_info, discover_plugins
        
        for plugin_name in discover_plugins():
            plugin_info = get_plugin_info(plugin_name)
            if plugin_info and "domains" in plugin_info:
                for domain in plugin_info["domains"]:
                    domain_name = domain.get("name")
                    if domain_name:
                        register_package_for_domain(domain_name, plugin_name)
                        logger.info(f"Registered plugin '{plugin_name}' for domain '{domain_name}'")
    except ImportError:
        logger.warning("Plugin system not available")

# Automatically discover domains when this module is loaded
discover_domains()
