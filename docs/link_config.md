# LinkConfig Documentation

The LinkConfig system provides a structured approach to configuring and validating link steps within a Chain. This document covers how to work with LinkConfig objects, create specialized configuration models for different link types, and integrate them into your chains.

## Table of Contents
- [Introduction](#introduction)
- [Basic Usage](#basic-usage)
- [Specialized Link Configurations](#specialized-link-configurations)
- [Validation](#validation)
- [Integration with Chain](#integration-with-chain)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Introduction

LinkConfig is a Pydantic model that defines the structure and validation rules for step configurations in a Chain. It provides better type safety, clearer documentation, and improved error handling compared to using raw dictionaries.

Benefits of using LinkConfig:
- **Type Safety**: Static type checking helps catch configuration errors early
- **Auto-completion**: IDE support for field names and properties
- **Validation**: Automatic validation of required fields and types
- **Documentation**: Self-documenting code through type annotations
- **Extensibility**: Easily create specialized configuration types

## Basic Usage

### Creating a LinkConfig

```python
from chain import LinkConfig

# Create a basic configuration
config = LinkConfig(
    name="MyStep",
    type="llm",
    description="Generate a response using an LLM",
    parameters={
        "prompt": "Tell me about {topic}",
        "topic": "artificial intelligence"
    },
    output_format="json",
    output_schema={
        "response": {
            "type": "string",
            "description": "The generated response"
        }
    }
)
```

### Converting Between Dict and LinkConfig

```python
# Convert from dict to LinkConfig
config_dict = {
    "name": "MyStep",
    "type": "llm",
    "parameters": {"prompt": "Hello world"}
}
config = LinkConfig(**config_dict)

# Convert back to dict
dict_data = config.dict()
```

### Core LinkConfig Fields

| Field | Type | Description |
|-------|------|-------------|
| name | str | Unique name for the step (required) |
| type | str | Type of link to use (required) |
| description | str | Human-readable description of this step |
| parameters | Dict[str, Any] | Parameters to pass to the link |
| output_format | str | Expected output format (e.g., "json", "text") |
| output_schema | Dict[str, Any] | Schema definition for validating output |

## Specialized Link Configurations

Each link type has its own specialized configuration class that extends LinkConfig with type-specific fields.

### LLM Link Configuration

```python
from links.llm_link import LLMLinkConfig

llm_config = LLMLinkConfig(
    name="GenerateResponse",
    type="llm",
    model="gpt-4",
    temperature=0.7,
    max_tokens=500,
    prompt="Generate a response about {topic}",
    parameters={"topic": "Machine Learning"},
    output_format="json",
    output_schema={
        "content": {"type": "string"}
    }
)
```

### User Input Configuration

```python
from links.user_input_link import UserInputLinkConfig

input_config = UserInputLinkConfig(
    name="GetUserPreferences",
    type="user_input",
    description="Collect user preferences",
    inputs={
        "topic": {
            "description": "What topic are you interested in?",
            "required": True
        },
        "detail_level": {
            "description": "How detailed should the response be? (1-5)",
            "type": "number",
            "min": 1,
            "max": 5,
            "default": 3
        }
    }
)
```

### SQL Link Configuration

```python
from links.sql_link import SQLLinkConfig

sql_config = SQLLinkConfig(
    name="QueryProducts",
    type="sql",
    query="SELECT * FROM products WHERE category = '{category}'",
    database_url="sqlite:///database.db",
    parameters={"category": "electronics"}
)
```

### Agent Link Configuration

```python
from links.agent_link import AgentLinkConfig

agent_config = AgentLinkConfig(
    name="ResearchAgent",
    type="agent",
    task="Research {topic} and provide a summary",
    model="gpt-4",
    parameters={"topic": "quantum computing"},
    tools=[
        {
            "name": "search",
            "type": "web",
            "description": "Search the web for information"
        }
    ]
)
```

### Configuration Field Reference

#### LLMLinkConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| model | str | DEFAULT_LLM_MODEL | LLM model to use (e.g., "gpt-4") |
| temperature | float | 0.7 | Randomness of generation (0-1) |
| max_tokens | int | 1500 | Maximum tokens to generate |
| prompt | str | None | Direct prompt text to use |
| template | str | None | Template file path to load prompt from |
| output_key | str | "result" | Key to store output under |
| execution_method | str | "direct" | Method to use ("direct" or "chain") |

#### UserInputLinkConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| inputs | Dict | None | Input field definitions |
| input | Dict | None | Alternative to inputs |
| template | str | None | Template for input instructions |
| template_file | str | None | File path for instructions template |
| default_values | Dict | None | Default values if no input provided |

#### SQLLinkConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| query | str | Required | SQL query text or file path (.sql) |
| database_url | str | None | Database connection string |

#### AgentLinkConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| task | str | Required | The task for the agent to perform |
| model | str | DEFAULT_LLM_MODEL | LLM model for the agent |
| temperature | float | 0.7 | Temperature for agent responses |
| tools | List[Dict] | [] | List of tools the agent can use |
| agent_type | str | "CONVERSATIONAL_REACT_DESCRIPTION" | Agent type to use |

## Validation

LinkConfig objects are validated using Pydantic's validation system plus custom validation logic in each link type.

### General Validation

Basic validation ensures required fields are present and have the right types:

```python
# This will raise a ValidationError because 'name' is required
try:
    config = LinkConfig(type="llm")
except Exception as e:
    print(f"Validation error: {e}")
```

### Link-Specific Validation

Each link type has its own validation logic implemented in the `_validate_config_impl` method:

```python
# This will fail LLM-specific validation because neither prompt nor template is provided
try:
    link_handler = LLMLink()
    config = LinkConfig(name="MyStep", type="llm")
    link_handler.validate_config(config)
except Exception as e:
    print(f"LLM validation error: {e}")
```

### Common Validation Rules

| Link Type | Validation Rules |
|-----------|------------------|
| LLM | Must have either `prompt` or `template` |
| SQL | Must have `query` |
| Agent | Must have `task` |
| User Input | Must have `inputs`, `input`, template-related field, or output_schema |

## Integration with Chain

The Chain class now works directly with LinkConfig objects:

```python
from chain import Chain, LinkConfig
from links.user_input_link import UserInputLinkConfig
from links.llm_link import LLMLinkConfig

# Create step configurations
steps = [
    UserInputLinkConfig(
        name="GetQuery",
        type="user_input",
        inputs={"query": {"description": "Enter your question"}}
    ),
    LLMLinkConfig(
        name="GenerateAnswer",
        type="llm",
        model="gpt-4",
        prompt="Question: {query}\nAnswer:",
        parameters={"query": "{{GetQuery_output.data.query}}"}
    )
]

# Create the chain
recipe_data = {
    "name": "Q&A Chain",
    "version": "1.0",
    "steps": [step.dict() for step in steps]  # Convert to dict for storage
}

chain = Chain(recipe_data)  # Chain will convert back to LinkConfig internally

# Execute the chain
results = chain.execute()
```

### Parameter Resolution with LinkConfig

The Chain's parameter resolution system works seamlessly with LinkConfig objects:

```python
import yaml

# YAML with parameter references
yaml_content = """
name: Parameter Example
steps:
  - name: UserInput
    type: user_input
    inputs:
      topic:
        description: "Enter a topic:"
  
  - name: GenerateContent
    type: llm
    model: gpt-4
    prompt: "Write about {topic}"
    parameters:
      topic: "{{UserInput_output.data.topic}}"
"""

# Load and create chain
recipe = yaml.safe_load(yaml_content)
chain = Chain(recipe)

# Chain will internally resolve parameters between LinkConfig objects
results = chain.execute()
```

## Best Practices

1. **Use specialized config classes**: Always use the specialized LinkConfig subclass for your link type (e.g., LLMLinkConfig for LLM links)

2. **Validate before execution**: Call `validate_config()` on your link handlers during development to catch configuration errors early

3. **Document required parameters**: Clearly document which parameters are required for each link type

4. **Use type hints**: Take advantage of IDE type hints by using the specialized config classes

5. **Keep backward compatibility**: When possible, design links to accept both LinkConfig objects and plain dictionaries

6. **Add descriptive defaults**: Use sensible defaults and include descriptions in Field definitions

7. **Test configuration validation**: Include unit tests that verify your validation logic rejects invalid configurations

## Common Patterns

### Creating a Custom Link Type

When creating a custom link type, start by defining its configuration model:

```python
from chain import LinkConfig
from pydantic import Field

class MyCustomLinkConfig(LinkConfig):
    """Configuration for my custom link type"""
    api_key: str
    endpoint: str = "https://api.example.com"
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    cache_results: bool = True
```

Then implement the link with proper validation:

```python
from links.base_link import BaseLink

class MyCustomLink(BaseLink):
    def get_required_fields(self) -> list:
        return ["name", "type", "api_key"]
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        # Check if using specialized config
        if isinstance(config, MyCustomLinkConfig):
            if not config.api_key:
                raise ValueError("API key is required")
        else:
            # Handle regular LinkConfig
            config_dict = config.dict()
            parameters = config.parameters or {}
            
            # Check for api_key in various possible locations
            api_key = config_dict.get("api_key") or parameters.get("api_key")
            if not api_key:
                raise ValueError("API key is required")
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        # Extract configuration
        if isinstance(config, MyCustomLinkConfig):
            # Directly access specialized fields
            api_key = config.api_key
            endpoint = config.endpoint
            max_retries = config.max_retries
        else:
            # Extract from regular LinkConfig
            config_dict = config.dict()
            parameters = config.parameters or {}
            
            # Get values with fallbacks
            api_key = config_dict.get("api_key") or parameters.get("api_key")
            endpoint = config_dict.get("endpoint", "https://api.example.com")
            max_retries = config_dict.get("max_retries", 3)
        
        # Implementation logic here
        # ...
        
        return {"result": "Success"}
```

### Using Environment Variables with LinkConfig

You can use environment variables in your LinkConfig objects:

```python
import os
from pydantic import BaseSettings, Field
from chain import LinkConfig

# Create a settings model
class APISettings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")
    endpoint: str = Field("https://api.example.com", env="API_ENDPOINT")

# Create a config that uses settings
class APILinkConfig(LinkConfig):
    settings: Optional[APISettings] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.settings:
            self.settings = APISettings()

# Usage
config = APILinkConfig(
    name="APICall",
    type="api"
)
# Now config.settings.api_key will have the value from the API_KEY env var
```

### Conditional Configuration

You can create configurations that adapt based on other parameters:

```python
def create_adaptive_config(user_level):
    """Create a configuration adapted to user expertise level"""
    
    # Base configuration
    config = LLMLinkConfig(
        name="GenerateContent",
        type="llm",
        model="gpt-4"
    )
    
    # Adapt based on user level
    if user_level == "beginner":
        config.prompt = "Explain {topic} in simple terms a beginner would understand"
        config.parameters = {"topic": "{{topic}}"}
    elif user_level == "intermediate":
        config.prompt = "Explain {topic} with some technical details appropriate for intermediate users"
        config.parameters = {"topic": "{{topic}}"}
    else:  # advanced
        config.prompt = "Provide an in-depth technical explanation of {topic} with advanced concepts"
        config.parameters = {"topic": "{{topic}}"}
    
    return config
```

### Configuration Templates

You can create function templates for common configuration patterns:

```python
def create_qa_chain(model="gpt-4", temperature=0.7):
    """Create a standard Q&A chain with the specified model"""
    
    steps = [
        UserInputLinkConfig(
            name="GetQuestion",
            type="user_input",
            inputs={"question": {"description": "What would you like to know?"}}
        ),
        LLMLinkConfig(
            name="GenerateAnswer",
            type="llm",
            model=model,
            temperature=temperature,
            prompt="Question: {question}\n\nProvide a detailed, accurate answer:",
            parameters={"question": "{{GetQuestion_output.data.question}}"}
        )
    ]
    
    recipe_data = {
        "name": "Q&A Chain",
        "version": "1.0",
        "steps": [step.dict() for step in steps]
    }
    
    return Chain(recipe_data)
```

## Technical Details

### BaseLink and LinkConfig Interaction

The BaseLink class has been updated to handle LinkConfig objects:

```python
def execute(self, config: Union[LinkConfig, Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
    """Template method for executing a link with either dict or LinkConfig"""
    # Convert dict to LinkConfig if necessary
    link_config = self._ensure_link_config(config)
    
    # Validate the configuration
    self.validate_config(link_config)
    
    # Execute with validated config
    result = self._execute_impl(link_config, context)
    
    # Format and return output
    return self.format_output(result=result)

def _ensure_link_config(self, config: Union[LinkConfig, Dict[str, Any]]) -> LinkConfig:
    """Ensure we have a LinkConfig object, converting from dict if needed"""
    if isinstance(config, LinkConfig):
        return config
    
    # Convert dict to LinkConfig
    try:
        return LinkConfig(**config)
    except ValidationError:
        # Fallback minimal config
        return LinkConfig(
            name=config.get('name', 'unnamed_step'),
            type=config.get('type', 'unknown_type')
        )
```

### Lifecycle of a LinkConfig Object

1. **Creation**: LinkConfig objects are created either directly in code or by converting dictionary configurations
2. **Parameter Resolution**: The Chain resolves parameters from previous steps using `_resolve_parameters_in_config()`
3. **Validation**: The link handler validates the configuration using `validate_config()`
4. **Execution**: The link executes using the validated configuration
5. **Output Processing**: The link handler formats and returns the execution result

This lifecycle ensures that configurations are properly validated and resolved before execution, increasing reliability and making errors easier to diagnose.
