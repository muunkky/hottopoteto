"""
CLI commands for recipes
"""
import os
import logging
from pathlib import Path
import json
import yaml
import inquirer
from core.links import list_link_types, get_link_handler

logger = logging.getLogger(__name__)

def add_recipes_command(subparsers):
    """Add recipes command to the CLI."""
    parser = subparsers.add_parser("recipes", help="Manage recipes")
    sub = parser.add_subparsers(dest="recipes_command", required=True)
    
    # Create recipe command
    create_parser = sub.add_parser("create", help="Create a new recipe")
    create_parser.add_argument("--name", help="Recipe name")
    create_parser.add_argument("--domain", help="Primary domain")
    create_parser.add_argument("--interactive", action="store_true", 
                              help="Use interactive wizard")
    
    # Validate recipe command
    validate_parser = sub.add_parser("validate", help="Validate a recipe")
    validate_parser.add_argument("recipe_file", help="Path to recipe file")
    
    # Generate recipe from template
    generate_parser = sub.add_parser("generate", help="Generate a recipe from template")
    generate_parser.add_argument("--link-type", help="Link type to generate template for")
    generate_parser.add_argument("--output", help="Output file path")

def handle_recipes_command(args):
    """Handle recipes command."""
    if args.recipes_command == "create":
        if args.interactive:
            _interactive_recipe_creator(args)
        else:
            _create_recipe(args)
    elif args.recipes_command == "validate":
        _validate_recipe(args.recipe_file)
    elif args.recipes_command == "generate":
        _generate_recipe_template(args)

def _interactive_recipe_creator(args):
    """Interactive recipe creation wizard."""
    print("🧙‍♂️ Welcome to the Recipe Creation Wizard!")
    
    # Collect basic recipe info
    questions = [
        inquirer.Text('name', message="Recipe name"),
        inquirer.Text('description', message="Recipe description"),
        inquirer.Text('version', message="Version", default="1.0.0"),
        inquirer.Text('domain', message="Primary domain", default="generic"),
    ]
    
    answers = inquirer.prompt(questions)
    
    # Initialize recipe
    recipe = {
        "name": answers['name'],
        "description": answers['description'],
        "version": answers['version'],
        "domain": answers['domain'],
        "links": []
    }
    
    # Add links interactively
    while True:
        # Ask if user wants to add another link
        add_link = inquirer.confirm("Add a link to the recipe?", default=True)
        if not add_link:
            break
            
        # Get available link types
        available_link_types = list_link_types()
        
        # Collect link info
        link_questions = [
            inquirer.Text('name', message="Link name"),
            inquirer.List('type', message="Link type", 
                          choices=available_link_types),
        ]
        
        link_answers = inquirer.prompt(link_questions)
        
        # Get link handler to determine additional fields
        link_handler = get_link_handler(link_answers['type'])
        link_schema = link_handler.get_schema() if link_handler else {}
        
        # Create basic link
        link = {
            "name": link_answers['name'],
            "type": link_answers['type']
        }
        
        # Add link to recipe
        recipe["links"].append(link)
    
    # Save recipe
    if not args.name:
        filename = f"{answers['name'].lower().replace(' ', '_')}.yaml"
    else:
        filename = f"{args.name}.yaml"
    
    output_path = os.path.join("templates", "recipes", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.dump(recipe, f)
        
    print(f"✅ Recipe created at {output_path}")

# ...additional helper functions...
