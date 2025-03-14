# Adding a Custom "Trace" Logging Level with Purple Color

This guide explains how to add a custom logging level called "Trace" to your Python application, and configure it to display in purple/magenta in the console output.

## Prerequisites

*   Python 3.6 or higher
*   `colorama` package (for color support on Windows)

    ```bash
    pip install colorama
    ```

## Steps

1.  **Modify `main.py`:**

    *   Open your `main.py` file.
    *   Add the following code at the beginning of the file, after the existing imports:

    ```python
    # filepath: c:\Users\Cameron\Projects\langchain\v2\main.py
    import logging

    # Define a custom logging level
    TRACE = 15  # Between DEBUG (10) and INFO (20)
    logging.addLevelName(TRACE, "TRACE")

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, **kws)

    logging.Logger.trace = trace
    ```

    **Explanation:**

    *   We define a new logging level called `TRACE` with a numeric value of 15. This places it between `DEBUG` (10) and `INFO` (20) in terms of severity.
    *   We use `logging.addLevelName` to associate the name "TRACE" with the numeric value.
    *   We add a `trace` method to the `logging.Logger` class, allowing you to call `logging.getLogger().trace()` to log messages at the `TRACE` level.

2.  **Add Color Formatting:**

    *   Modify the `CustomFormatter` class in `main.py` to include a color for the `TRACE` level. Replace your existing `CustomFormatter` class with the following:

    ```python
    # filepath: c:\Users\Cameron\Projects\langchain\v2\main.py
    class CustomFormatter(logging.Formatter):
        grey = "\x1b[38;20m"
        purple = "\x1b[35;20m"  # Magenta/Purple color code
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        reset = "\x1b[0m"
        format_str = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

        FORMATS = {
            logging.DEBUG: grey + format_str + reset,
            logging.INFO: grey + format_str + reset,
            TRACE: purple + format_str + reset,
            logging.WARNING: yellow + format_str + reset,
            logging.ERROR: red + format_str + reset,
            logging.CRITICAL: red + format_str + reset
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
    ```

    **Explanation:**

    *   We added a `purple` variable containing the ANSI escape code for magenta/purple.
    *   We added an entry for `TRACE` in the `FORMATS` dictionary, assigning it the purple color code.

3.  **Using the New Logging Level:**

    *   Now you can use the `TRACE` logging level in your code:

    ```python
    # filepath: c:\Users\Cameron\Projects\langchain\v2\your_module.py
    import logging

    logger = logging.getLogger(__name__)

    def some_function():
        logger.trace("This is a trace message.")
        # ... your code ...
    ```

    **Explanation:**

    *   Import the `logging` module.
    *   Get a logger instance using `logging.getLogger(__name__)`.
    *   Use `logger.trace()` to log messages at the `TRACE` level.

4.  **Verify the Output:**

    *   Run your application.
    *   You should see the "Trace" messages displayed in purple/magenta in your console output.

## Complete `main.py` Example

Here's a complete example of how your `main.py` file should look after applying these changes:

```python
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
        self._log(TRACE, message, args, **kws)

logging.Logger.trace = trace

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    purple = "\x1b[35;20m"  # Magenta/Purple color code
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        TRACE: purple + format_str + reset,
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

    # Set up prompt directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(project_dir, "prompts")

    # Configure BaseLink to use the prompt directory
    BaseLink.set_prompt_directory(prompt_dir)

    # Create and execute chain from recipe file
    logging.info(f"Starting chain execution from recipe: {recipe_path}")
    chain = Chain.from_recipe_file(recipe_path)
    results = chain.execute()
    logging.info("Chain execution completed.")

    # Display results with standardized formatting
    print("\n===== CHAIN EXECUTION RESULTS =====")

    for key, value in results.items():
        # Skip internal metadata key
        if key == "__chain_metadata__":
            continue
        logging.debug(f"Processing key: {key}")
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

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled.")

    recipe_file = args.recipe
    if not recipe_file.endswith(".yaml"):
        recipe_file += ".yaml"
    recipe_path = f"recipes/{recipe_file}"
    run_recipe(recipe_path)