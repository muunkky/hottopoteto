# Creating Recipes in LangChain V2

This guide explains how to create recipes in LangChain V2, including recipe structure, link configuration, and best practices.

## Recipe Overview

Recipes are YAML files that define a sequence of operations (links) to execute. They specify:

- Metadata about the recipe
- Links to execute
- Configuration for each link
- Input and output schemas

## Basic Recipe Structure

```yaml
name: "My Recipe"
description: "Description of what this recipe does"
version: "1.0"
domain: "example_domain"  # Optional domain association
links:
  - name: "Link_1"
    type: "link_type"
    # link-specific configuration
  - name: "Link_2"
    type: "another_link_type"
    # link-specific configuration
```

## Creating a Basic Recipe

Let's create a simple recipe that uses an LLM to answer a question:

```yaml
name: "Simple Question Answerer"
description: "Uses an LLM to answer a user question"
version: "1.0"
links:
  - name: "Get_Question"
    type: "user_input"
    description: "Get the user's question"
    inputs:
      question:
        type: "string"
        description: "What would you like to know?"
    output_schema:
      properties:
        question:
          type: "string"
          description: "The user's question"
      required:
        - question

  - name: "Generate_Answer"
    type: "llm"
    model: "gpt-4o"
    temperature: 0.7
    prompt: "Please answer this question: {{ Get_Question.data.question }}"
```

## Link Types

Different link types require different configuration:

### User Input Links

```yaml
- name: "User_Input"
  type: "user_input"
  description: "Collect information from the user"
  inputs:
    name:
      type: "string"
      description: "Your name"
    age:
      type: "number"
      description: "Your age"
    favorite_color:
      type: "select"
      description: "Your favorite color"
      options:
        - value: "red"
          description: "Red"
        - value: "blue"
          description: "Blue"
        - value: "green"
          description: "Green"
  output_schema:
    properties:
      name:
        type: "string"
      age:
        type: "integer"
      favorite_color:
        type: "string"
    required:
      - name
      - age
```

### LLM Links

```yaml
- name: "LLM_Link"
  type: "llm"
  model: "gpt-4o"  # Model to use
  temperature: 0.7  # Creativity (0.0-1.0)
  token_limit: 500  # Maximum tokens to generate
  
  # Direct prompt approach
  prompt: "Write a poem about {{ User_Input.data.favorite_color }}"
  
  # Or template approach
  template:
    file: "poem_template.txt"
    inputs:
      subject: "{{ User_Input.data.favorite_color }}"
      style: "sonnet"
  
  # Output schema for structured responses
  output_schema:
    properties:
      title:
        type: "string"
      poem:
        type: "string"
    required:
      - poem
```

### Function Links

```yaml
- name: "Function_Link"
  type: "function"
  description: "Process data with a function"
  
  # Using a registered function
  function:
    name: "calculate_statistics"
  
  # Or direct code execution
  function:
    language: "python"
    code: "return {'result': len(input_text) * multiplier}"
  
  # Function inputs
  inputs:
    input_text: "{{ User_Input.data.name }}"
    multiplier: 5
    
  output_schema:
    properties:
      result:
        type: "integer"
    required:
      - result
```

### Storage Links

```yaml
- name: "Storage_Link"
  type: "storage"
  operation: "store"  # store, retrieve, update, delete, search
  adapter:
    type: "file"  # file, sqlite, mongodb
    config:
      base_dir: "data/storage"
  data:
    name: "{{ User_Input.data.name }}"
    preferences:
      color: "{{ User_Input.data.favorite_color }}"
  output_schema:
    properties:
      id:
        type: "string"
      stored:
        type: "boolean"
    required:
      - id
      - stored
```

## Advanced Recipe Features

### Conditional Execution

```yaml
- name: "Conditional_Link"
  type: "llm"
  condition: "{{ User_Input.data.age > 18 }}"
  # This link only executes if the condition is true
  prompt: "Write content for adults"
```

### Conversation Context

```yaml
- name: "Chat_Link"
  type: "llm"
  conversation: "chat_session"  # Maintains conversation history
  prompt: "Continue our conversation about {{ topic }}"
```

### References to Previous Links

You can reference outputs from previous links using template syntax:

```yaml
- name: "Generate_Summary"
  type: "llm"
  prompt: |
    Summarize these details:
    Name: {{ User_Input.data.name }}
    Age: {{ User_Input.data.age }}
    Color preference: {{ User_Input.data.favorite_color }}
```

## Schema Validation

Use output schemas to validate and structure responses:

```yaml
output_schema:
  properties:
    name:
      type: "string"
    score:
      type: "integer"
      minimum: 0
      maximum: 100
    categories:
      type: "array"
      items:
        type: "string"
  required:
    - name
    - score
```

## Templates

For longer prompts, use template files instead of inline prompts:

1. Create a template file in the `prompts` directory:
