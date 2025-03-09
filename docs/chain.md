# Chain Documentation

The Chain system is a flexible framework for creating complex workflows by chaining together different types of processing steps (links). Each link represents a specific operation such as running an LLM query, executing a SQL command, getting user input, or running an agent with tools.

## Table of Contents
- [Overview](#overview)
- [Key Concepts](#key-concepts)
- [Getting Started](#getting-started)
- [Creating Chains](#creating-chains)
- [Link Types](#link-types)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)

## Overview

A Chain consists of multiple steps (links) that are executed sequentially. Each step can use the outputs from previous steps as inputs, creating a flexible pipeline for data processing and generation. Chains can be defined using YAML recipes or constructed programmatically using Python.

## Key Concepts

- **Chain**: A sequence of processing steps defined in a recipe
- **Link**: An individual processing step in a chain (e.g., LLM, SQL, User Input, Agent)
- **LinkConfig**: Configuration model for steps, providing structure and validation
- **Recipe**: A YAML or JSON definition of a chain and its steps
- **Context**: The shared state that steps can read from and write to during execution

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/langchain-v2.git
cd langchain-v2

# Install required dependencies
pip install -r requirements.txt
```

### Basic Example

Here's a simple example that creates a chain with a user input step and an LLM step:

```python
from chain import Chain

# Load a chain from a recipe file
my_chain = Chain.from_recipe_file("recipes/simple_qa.yaml")

# Execute the chain
results = my_chain.execute()

# Access the outputs
final_answer = results["GenerateAnswer_output"]["data"]["result"]
print(final_answer)
```

## Creating Chains

Chains can be created in two primary ways:

### 1. Using YAML Recipe Files

YAML recipes are the most common way to define chains. They're easy to read, modify, and share.

```yaml
name: Simple Q&A Chain
version: 1.0
description: Answers user questions using an LLM
steps:
  - name: UserQuestion
    type: user_input
    description: "Ask your question"
    inputs:
      question:
        description: "What would you like to know?"
        required: true
  
  - name: GenerateAnswer
    type: llm
    model: gpt-4
    temperature: 0.7
    prompt: "Question: {question}\n\nPlease provide a detailed answer:"
    parameters:
      question: "{{UserQuestion_output.data.question}}"
```

### 2. Using Python Code with LinkConfig

You can also create chains programmatically using the LinkConfig model:

```python
from chain import Chain, LinkConfig
from links.user_input_link import UserInputLinkConfig
from links.llm_link import LLMLinkConfig

# Create step configurations
user_input_config = UserInputLinkConfig(
    name="UserQuestion",
    type="user_input",
    description="Ask your question",
    inputs={
        "question": {
            "description": "What would you like to know?",
            "required": True
        }
    }
)

llm_config = LLMLinkConfig(
    name="GenerateAnswer",
    type="llm",
    model="gpt-4",
    temperature=0.7,
    prompt="Question: {question}\n\nPlease provide a detailed answer:",
    parameters={
        "question": "{{UserQuestion_output.data.question}}"
    }
)

# Create the chain
recipe_data = {
    "name": "Simple Q&A Chain",
    "version": "1.0",
    "description": "Answers user questions using an LLM",
    "steps": [
        user_input_config.dict(),
        llm_config.dict()
    ]
}

chain = Chain(recipe_data)

# Execute the chain
results = chain.execute()
```

## Link Types

The system includes several built-in link types:

### User Input Link

Collects input from users through the command line.

```yaml
- name: UserInput
  type: user_input
  description: "Collect user preferences"
  inputs:
    query:
      description: "What would you like to know about?"
      required: true
    depth:
      description: "How detailed should the answer be? (1-5)"
      type: number
      min: 1
      max: 5
      default: 3
```

### LLM Link

Interfaces with language models like GPT-4.

```yaml
- name: GenerateText
  type: llm
  model: gpt-4
  temperature: 0.7
  prompt: "Generate a paragraph about {topic} at complexity level {level}."
  parameters:
    topic: "{{UserInput_output.data.topic}}"
    level: "{{UserInput_output.data.level}}"
  output_format: json
  output_schema:
    content:
      type: string
      description: "The generated paragraph"
    keywords:
      type: array
      description: "Key concepts in the paragraph"
```

### SQL Link

Executes SQL queries against databases.

```yaml
- name: QueryDatabase
  type: sql
  query: "SELECT * FROM products WHERE category = '{category}' LIMIT {limit}"
  parameters:
    category: "{{UserInput_output.data.category}}"
    limit: 10
  database_url: "sqlite:///my_database.db"
```

### Agent Link

Runs LangChain agents with tools.

```yaml
- name: ResearchAgent
  type: agent
  task: "Research information about {topic} and summarize the findings"
  parameters:
    topic: "{{UserInput_output.data.topic}}"
  model: gpt-4
  agent_type: ZERO_SHOT_REACT_DESCRIPTION
  tools:
    - name: search
      type: web
      description: "Search the web for information"
```

## Advanced Features

### Parameter Resolution

You can reference outputs from previous steps in your chain using the `{{step_name_output.data.field}}` syntax:

```yaml
parameters:
  user_query: "{{UserInput_output.data.query}}"
  products: "{{QueryDatabase_output.data.result}}"
```

### Output Schema Validation

Define expected output structures for validation:

```yaml
output_schema:
  summary:
    type: string
    description: "Brief summary of the analysis"
  data_points:
    type: array
    description: "Key data points"
  confidence:
    type: number
    description: "Confidence score from 0-1"
```

### Custom Link Types

You can register custom link types:

```python
from chain import Chain
from my_custom_link import MyCustomLink

# Register a custom link type
Chain.register_link("custom", MyCustomLink())

# Now you can use it in your recipes
# - name: CustomStep
#   type: custom
#   ...
```

## API Reference

### Chain Class

```python
class Chain:
    @classmethod
    def from_recipe_file(cls, filepath: str) -> 'Chain'
    @classmethod
    def register_link(cls, link_type: str, link_handler: BaseLink) -> None
    @classmethod
    def get_available_links(cls) -> List[str]
    
    def __init__(self, recipe_data: Dict[str, Any])
    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
```

### LinkConfig Models

```python
# Base LinkConfig
class LinkConfig(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    output_format: Optional[str] = None
    output_schema: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
# LLM-specific config
class LLMLinkConfig(LinkConfig):
    model: str = DEFAULT_LLM_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_TOKEN_LIMIT
    prompt: Optional[str] = None
    template: Optional[str] = None
    output_key: str = "result"
    execution_method: str = "direct"
```

## Best Practices

1. **Use descriptive step names**: Choose names that clearly indicate what the step does
2. **Validate output schemas**: Define output schemas for steps to ensure data consistency
3. **Handle errors gracefully**: Chains continue execution even if individual steps fail
4. **Use specialized LinkConfig models**: For better type safety and validation
5. **Keep steps focused**: Each step should do one thing well
6. **Use templates for complex prompts**: Store large prompts in separate template files
7. **Log execution contexts**: Enable DEBUG logging to see full context during development

## Example Recipes

You can find more examples in the `examples/` directory of the repository.