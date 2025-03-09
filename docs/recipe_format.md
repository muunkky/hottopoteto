# LangChain Recipe Format Documentation

LangChain recipes are YAML files that define a sequence of steps to be executed. Each step uses a specific "link" type 
(llm, sql, agent, user_input) to perform different operations.

## Recipe Structure

A recipe consists of:

- `name` (optional): A name for the recipe
- `version` (optional): Version number (e.g., "1.0.0")
- `description` (optional): Description of what the recipe does
- `steps` (required): An array of step definitions

Example:
