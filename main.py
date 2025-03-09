import logging
import os
import sys
import json
import argparse
from dotenv import load_dotenv
from chain import Chain
from links.base_link import BaseLink

# Load environment variables from .env file if it exists
print("Loading .env file...")
load_dotenv()

# Set logging to DEBUG level for more detailed information
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def format_output_for_display(output):
    """Format link output for display, extracting from standardized format if needed."""
    if isinstance(output, dict):
        if "success" in output and "data" in output:
            # This is our standard format
            if output["success"]:
                return output["data"]
            else:
                return f"ERROR: {output.get('error', 'Unknown error')}"
        else:
            # Regular dict
            return output
    return output

def run_recipe(recipe_path: str):
    """
    Runs a recipe from a YAML configuration file.
    
    Args:
        recipe_path (str): Path to the recipe YAML file.
    """
    logging.info(f"Loading recipe from: {recipe_path}")

    # Set up prompt directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(project_dir, "prompts")
    
    # Configure BaseLink to use the prompt directory
    BaseLink.set_prompt_directory(prompt_dir)
    logging.debug(f"Using prompt directory: {prompt_dir}")

    # Create and execute chain from recipe file
    chain = Chain.from_recipe_file(recipe_path)
    results = chain.execute()
    
    # Log results with standardized formatting
    logging.info("\n==== FINAL OUTPUT ====")
    print("\n===== CHAIN EXECUTION RESULTS =====")
    
    for key, value in results.items():
        # Skip internal metadata key
        if key == "__chain_metadata__":
            continue
            
        # Format and display result
        formatted_value = format_output_for_display(value)
        if isinstance(formatted_value, dict):
            try:
                # Pretty print dicts
                print(f"\n{key}:")
                print(json.dumps(formatted_value, indent=2))
            except:
                print(f"{key}: {formatted_value}")
        else:
            print(f"{key}: {formatted_value}")
    print("==================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a recipe from a YAML configuration file.")
    parser.add_argument(
        "-r", "--recipe",
        type=str,
        help="The name of the recipe file located in the recipes/ folder."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging"
    )
    args = parser.parse_args()
    
    # Configure logging based on command line arguments
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug logging enabled")
    else:
        logging.getLogger().setLevel(logging.INFO)

    recipe_file = args.recipe
    if not recipe_file.endswith(".yaml"):
        recipe_file += ".yaml"
    recipe_path = f"recipes/{recipe_file}"
    run_recipe(recipe_path)
