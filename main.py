import logging
from utils.config_loader import load_recipe
from chains.sequential_chain import execute_recipe
import argparse

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def run_recipe(recipe_path: str):
    """
    Runs a recipe from a YAML configuration file.
    
    Args:
        recipe_path (str): Path to the recipe YAML file.
    """
    logging.info(f"Loading recipe from: {recipe_path}")

    # Load recipe
    recipe = load_recipe(recipe_path)
    logging.debug(f"Recipe loaded: {recipe}")
    
    # Execute recipe
    results = execute_recipe(recipe)
    
    # Log results
    logging.info("Final Output:")
    for key, value in results.items():
        logging.info(f"{key}: {value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a recipe from a YAML configuration file.")
    parser.add_argument(
        "-r", "--recipe_file",
        type=str,
        help="The name of the recipe file located in the configs/ folder."
    )
    args = parser.parse_args()

    recipe_path = f"configs/{args.recipe_file}"
    run_recipe(recipe_path)
