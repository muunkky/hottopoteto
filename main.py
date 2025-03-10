# filepath: c:\Users\Cameron\Projects\langchain\v2\main.py
import os
import sys
import json
import argparse
import logging
from dotenv import load_dotenv
from chain import Chain
from links.base_link import BaseLink

# Define a custom logging level
TRACE = 15  # Between DEBUG (10) and INFO (20)
logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kws, stacklevel=2)

logging.Logger.trace = trace

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    purple = "\x1b[35;20m"  # Magenta/Purple color code
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(levelname)s - %(message)s"
    format_str_trace = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        TRACE: purple + format_str_trace + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Get the root logger
logger = logging.getLogger()

# Remove any existing handlers
if logger.hasHandlers():
    logger.handlers.clear()

# Create a handler that writes to the console
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

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
    logger.trace("Running recipe...")
    # Set up prompt directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(project_dir, "prompts")

    # Configure BaseLink to use the prompt directory
    BaseLink.set_prompt_directory(prompt_dir)

    # Create and execute chain from recipe file
    logger.info(f"Starting chain execution from recipe: {recipe_path}")
    chain = Chain.from_recipe_file(recipe_path)
    logger.trace(f"Chain created: {chain}")
    results = chain.execute()
    logger.info("Chain execution completed.")

    # Display results with standardized formatting
    print("\n===== CHAIN EXECUTION RESULTS =====")

    for key, value in results.items():
        # Skip internal metadata key
        if key == "__chain_metadata__":
            continue
        logger.debug(f"Processing key: {key}")
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
        help="Enable debug logger"
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    recipe_file = args.recipe
    if not recipe_file.endswith(".yaml"):
        recipe_file += ".yaml"
    recipe_path = f"recipes/{recipe_file}"
    logger.trace(f"Recipe path: {recipe_path}")
    run_recipe(recipe_path)