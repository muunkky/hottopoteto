# Logging in Hottopoteto

This document describes Hottopoteto's logging system, including the trace logger used for detailed debugging.

## Logging Levels

Hottopoteto uses Python's standard logging module with an additional custom level:

- **CRITICAL** (50): Critical errors that prevent the system from continuing
- **ERROR** (40): Errors that affect the current operation but allow the system to continue
- **WARNING** (30): Warnings about potential issues
- **INFO** (20): General information about system operation
- **TRACE** (15): Detailed information for debugging (custom level)
- **DEBUG** (10): Debugging information

## Trace Logger

The TRACE level (15) sits between INFO and DEBUG, providing a level for detailed tracing of operations without the verbosity of DEBUG:

```python
# Set up custom TRACE level
TRACE = 15  # between DEBUG and INFO
logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)

logging.Logger.trace = trace
```

## Using the Logger

```python
import logging

# Get a logger for your module
logger = logging.getLogger(__name__)

# Log at different levels
logger.debug("Debug information")
logger.trace("Detailed trace information")  # Custom level
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

## Configuration

Logging can be configured through environment variables or command-line options:

```bash
# Set logging level to TRACE
export HOTTOPOTETO_LOG_LEVEL=TRACE

# Run with debug logging
python main.py --debug execute --recipe_file path/to/recipe.yaml
```

## Viewing Logs

Logs are output to the console by default. For more persistent logging:

```bash
# Output logs to a file
python main.py execute --recipe_file path/to/recipe.yaml > recipe_run.log 2>&1
```

## Best Practices

1. **Appropriate Levels**: Use appropriate log levels based on importance
2. **Contextual Information**: Include relevant context in log messages
3. **Structured Data**: Use structured logging for machine-readable logs
4. **Performance**: Avoid expensive operations in log statements
