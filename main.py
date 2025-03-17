#!/usr/bin/env python3
import argparse
import json
import yaml
import os
import logging
import sys
import pkgutil
import importlib
from typing import Dict, Any, List

from core.executor import RecipeExecutor

# Import package commands
from cli.commands.packages import packages_group

def main():
    parser = argparse.ArgumentParser(description="Recipe Execution CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # execute command: Execute a recipe file
    execute_parser = subparsers.add_parser("execute", help="Execute a recipe file")
    execute_parser.add_argument("--recipe_file", type=str, required=True, help="Path to the recipe YAML/JSON file")
    execute_parser.add_argument("--output_dir", type=str, help="Directory to save recipe output")
    execute_parser.add_argument("--domain", type=str, help="Override the domain specified in the recipe")

    # list command: List all available recipes
    list_parser = subparsers.add_parser("list", help="List available recipes")
    list_parser.add_argument("--domain", type=str, help="Filter recipes by domain")

    # plugins command: Manage plugins
    plugins_parser = subparsers.add_parser("plugins", help="Manage plugins")
    plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command", required=True)
    
    # plugins list command
    plugins_list_parser = plugins_subparsers.add_parser("list", help="List available plugins")
    
    # plugins info command
    plugins_info_parser = plugins_subparsers.add_parser("info", help="Get information about a plugin")
    plugins_info_parser.add_argument("plugin_name", help="Name of the plugin")

    # domains command: Manage domains
    domains_parser = subparsers.add_parser("domains", help="Manage domains")
    domains_subparsers = domains_parser.add_subparsers(dest="domains_command", required=True)
    
    # domains list command
    domains_list_parser = domains_subparsers.add_parser("list", help="List available domains")
    
    # domains info command
    domains_info_parser = domains_subparsers.add_parser("info", help="Get information about a domain")
    domains_info_parser.add_argument("domain_name", help="Name of the domain")
    
    # domains packages command
    domains_packages_parser = domains_subparsers.add_parser("packages", help="List packages supporting a domain")
    domains_packages_parser.add_argument("domain_name", help="Name of the domain")

    # Register package commands
    # Create a subparser for packages commands
    packages_parser = subparsers.add_parser("packages", help="Manage packages")
    packages_subparsers = packages_parser.add_subparsers(dest="packages_command", required=True)
    
    # Add package commands to the subparser
    packages_subparsers.add_parser("list", help="List installed packages")
    
    install_parser = packages_subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package_name", help="Name of the package to install")
    install_parser.add_argument("--dev", action="store_true", help="Install in development mode")
    
    uninstall_parser = packages_subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("package_name", help="Name of the package to uninstall")
    
    create_parser = packages_subparsers.add_parser("create", help="Create a new package template")
    create_parser.add_argument("name", help="Name of the package")
    create_parser.add_argument("--domain", help="Include domain template")
    create_parser.add_argument("--plugin", help="Include plugin template")

    # Add domain-specific subcommands
    try:
        for domain_module_info in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "domains")]):
            domain_name = domain_module_info.name
            if domain_name != "__pycache__" and not domain_name.startswith("_"):
                try:
                    domain_module = importlib.import_module(f"domains.{domain_name}")
                    if hasattr(domain_module, "cli") and hasattr(domain_module.cli, "register_commands"):
                        domain_module.cli.register_commands(subparsers)
                except Exception as e:
                    logging.warning(f"Failed to register CLI commands for domain {domain_name}: {e}")
    except Exception as e:
        logging.warning(f"Failed to load domain-specific CLI commands: {e}")

    args = parser.parse_args()

    if args.command == "execute":
        # Load the recipe file
        try:
            with open(args.recipe_file, "r") as f:
                if args.recipe_file.endswith((".yaml", ".yml")):
                    recipe = yaml.safe_load(f)
                else:
                    recipe = json.load(f)
        except Exception as e:
            print(f"Failed to load recipe: {e}")
            return
            
        # Execute the recipe
        try:
            executor = RecipeExecutor(args.recipe_file)
            if args.domain:
                executor.domain = args.domain
                
            result = executor.execute()
            print(f"Recipe execution completed successfully.")
            
            # Save output if requested
            if args.output_dir:
                os.makedirs(args.output_dir, exist_ok=True)
                output_file = os.path.join(args.output_dir, f"{os.path.basename(args.recipe_file)}.output.json")
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Output saved to {output_file}")
                
        except Exception as e:
            print(f"Error executing recipe: {e}")
            
    elif args.command == "list":
        # List available recipes
        recipe_dir = "recipes"
        if args.domain:
            recipe_dir = os.path.join(recipe_dir, args.domain)
            
        if not os.path.exists(recipe_dir):
            print(f"Recipe directory not found: {recipe_dir}")
            return
            
        recipes = []
        for root, dirs, files in os.walk(recipe_dir):
            for file in files:
                if file.endswith((".yaml", ".yml", ".json")):
                    recipe_path = os.path.join(root, file)
                    recipes.append(recipe_path)
                    
        print(f"Found {len(recipes)} recipes:")
        for recipe in recipes:
            print(f"  {recipe}")

    elif args.command == "plugins":
        from plugins import discover_plugins, load_plugin, get_plugin_info
        
        if args.plugins_command == "list":
            plugins = discover_plugins()
            print(f"Found {len(plugins)} plugins:")
            for plugin in plugins:
                plugin_info = get_plugin_info(plugin)
                version = plugin_info.get("version", "unknown") if plugin_info else "unknown"
                print(f"  {plugin} (v{version})")
                
        elif args.plugins_command == "info":
            plugin_info = get_plugin_info(args.plugin_name)
            if plugin_info:
                print(f"Plugin: {args.plugin_name}")
                print(f"Version: {plugin_info.get('version', 'unknown')}")
                print(f"Description: {plugin_info.get('description', 'No description')}")
                
                if "requirements" in plugin_info:
                    print(f"Requirements:")
                    for req in plugin_info["requirements"]:
                        print(f"  - {req}")
                
                print("Entry points:")
                for entry_point_type, handlers in plugin_info.get("entry_points", {}).items():
                    print(f"  {entry_point_type}: {', '.join(handlers)}")
                
                if "domains" in plugin_info:
                    print("Supported domains:")
                    for domain in plugin_info["domains"]:
                        print(f"  - {domain}")
            else:
                print(f"Plugin '{args.plugin_name}' not found or not loaded")
    
    elif args.command == "domains":
        from core.domains import list_domains, get_domain_interface, get_packages_for_domain
        
        if args.domains_command == "list":
            domains = list_domains()
            print(f"Found {len(domains)} domains:")
            for domain in domains:
                print(f"  {domain}")
                
        elif args.domains_command == "info":
            domain_interface = get_domain_interface(args.domain_name)
            if domain_interface:
                print(f"Domain: {args.domain_name}")
                print(f"Version: {domain_interface.get('version', 'unknown')}")
                
                schemas = domain_interface.get('schemas', [])
                print(f"Schemas ({len(schemas)}):")
                for schema in schemas:
                    print(f"  - {schema.get('name')}")
                    
                functions = domain_interface.get('functions', [])
                print(f"Functions ({len(functions)}):")
                for function in functions:
                    print(f"  - {function.get('name')}")
                    
                packages = get_packages_for_domain(args.domain_name)
                print(f"Supported Packages ({len(packages)}):")
                for package in packages:
                    print(f"  - {package}")
            else:
                print(f"Domain '{args.domain_name}' not found")
        
        elif args.domains_command == "packages":
            packages = get_packages_for_domain(args.domain_name)
            if packages:
                print(f"Packages supporting domain '{args.domain_name}':")
                for package in packages:
                    print(f"  - {package}")
            else:
                print(f"No packages found for domain '{args.domain_name}'")
    
    # Add package command handler
    if args.command == "packages":
        from cli.commands.packages import list_packages, install_package, uninstall_package, create_package
        
        if args.packages_command == "list":
            list_packages()
        elif args.packages_command == "install":
            install_package(args.package_name, args.dev if hasattr(args, 'dev') else False)
        elif args.packages_command == "uninstall":
            uninstall_package(args.package_name)
        elif args.packages_command == "create":
            create_package(args.name, args.domain, args.plugin)

    # Handle domain-specific commands
    else:
        try:
            # Find the domain that registered this command
            for domain_module_info in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "domains")]):
                domain_name = domain_module_info.name
                if domain_name != "__pycache__" and not domain_name.startswith("_"):
                    try:
                        domain_module = importlib.import_module(f"domains.{domain_name}")
                        if hasattr(domain_module, "cli") and hasattr(domain_module.cli, "handle_command"):
                            # Try to handle the command with this domain
                            domain_module.cli.handle_command(args)
                            break
                    except Exception as e:
                        logging.warning(f"Error in domain {domain_name} CLI handling: {e}")
        except Exception as e:
            logging.error(f"Failed to handle domain-specific command: {e}")
            print(f"Error: {e}")

if __name__ == '__main__':
    main()