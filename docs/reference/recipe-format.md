# Recipe Format Reference

This document provides a detailed reference for creating recipes in Hottopoteto.

## Recipe Structure

A recipe is a YAML file that defines a workflow as a sequence of connected operations. Every recipe must follow this general structure:

```yaml
name: "Recipe Name"                # Required: Human-readable name
description: "Recipe description"   # Required: Brief description
version: "1.0"                      # Required: Semantic version
domain: "example_domain"            # Optional: Primary domain (defaults to "generic")
links:                              # Required: Sequence of operations to execute
  - name: "Link_1"                  # Required: Link identifier (used for references)
    type: "link_type"               # Required: Link type (e.g., "llm", "storage.save")
    # Link-specific configuration...
  - name: "Link_2"
    type: "another_link_type"
    # Link-specific configuration...
```

## Required Elements

Every recipe must include these elements:

- **name**: Human-readable identifier for the recipe
- **description**: Brief description of what the recipe does
- **version**: Semantic version number (e.g., "1.0.0")
- **links**: Array of link definitions that make up the recipe

## Optional Elements

Recipes can also include:

- **domain**: Primary domain for the recipe (defaults to "generic")
- **include**: Array of templates to include in this recipe
- **extends**: Template to extend with this recipe
- **tags**: Array of tags for categorization
- **metadata**: Additional metadata for the recipe
- **master_output_schema**: Schema that validates the entire recipe output

## Link Structure

Each link in a recipe requires these fields:

- **name**: Unique identifier for the link (used in references)
- **type**: Type of link to execute (e.g., "llm", "user_input", "storage.save")

Other fields depend on the link type. Common configurations include:

```yaml
# LLM Link Example
- name: "Generate_Text"
  type: "llm"
  model: "gpt-4o"                     # LLM model to use
  temperature: 0.7                     # Sampling temperature
  prompt: "Generate a {{subject}}."    # Text prompt with variables

# User Input Link Example
- name: "Get_User_Input"
  type: "user_input"
  inputs:
    name:
      type: "string"
      description: "Enter your name"
      required: true

# Storage Link Example
- name: "Save_Result"
  type: "storage.save"
  collection: "results"
  data: "{{ Generate_Text.data }}"
```

## Context References

Links can reference outputs from previous links using the syntax `{{ Link_Name.data.field_name }}`. For example:

```yaml
- name: "Format_Content"
  type: "llm"
  prompt: "Summarize this: {{ Generate_Text.data.raw_content }}"
```

## Template References

Recipes can reference external templates using the `template` field:

```yaml
- name: "Generate_Content"
  type: "llm"
  template:
    file: "domain/template_name.txt"   # Path to template file
    inputs:
      key: "{{ Previous_Link.data.value }}"
```

## Output Schema

Links can define expected output structure using JSON Schema:

```yaml
- name: "Generate_JSON"
  type: "llm"
  prompt: "Create JSON for a person"
  output_schema:
    type: "object"
    properties:
      name:
        type: "string"
      age:
        type: "integer"
    required: ["name", "age"]
```

## Conditional Execution

Links can be conditionally executed:

```yaml
- name: "Conditional_Step"
  type: "llm"
  condition: "{{ Previous_Link.data.should_continue == true }}"
  prompt: "This only runs if condition is true"
```

## Recipe Templates

### Including Templates

Include other recipe templates to reuse common patterns:

```yaml
name: "My Recipe"
description: "Recipe that uses templates"
version: "1.0"
includes:
  - template: "common/user_input.yaml"
  - template: "common/storage.yaml"
    
links:
  # Additional links here
```

### Extending Templates

Extend a base template to create a specialized version:

```yaml
name: "Extended Recipe"
description: "Recipe that extends a template"
version: "1.0"
extends: "base_recipe.yaml"

# Override or add links
links:
  - name: "Additional_Step"
    type: "llm"
    prompt: "Process the data further"
```

## Master Output Schema

Define a schema that validates the entire recipe output:

```yaml
master_output_schema:
  type: "object"
  properties:
    Step_1:
      type: "object"
      # Schema for Step_1 output
    Step_2:
      type: "object"
      # Schema for Step_2 output
  required: ["Step_1", "Step_2"]
```

## File Loading

Load external files in your recipes:

```yaml
- name: "Process_File"
  type: "function"
  function:
    name: "process_file"
  inputs:
    file_content: 
      $file: "path/to/file.txt"
```

## Special Variables

Recipes have access to special variables:

- **now()**: Current datetime
- **random()**: Random number between 0 and 1
- **random_int(min, max)**: Random integer in the specified range
- **uuid()**: Generate a UUID
- **env(name, default)**: Get environment variable with optional default

Example:

```yaml
- name: "Generate_With_Date"
  type: "llm"
  prompt: "Today is {{ now() | format_date('YYYY-MM-DD') }}"
```

## Best Practices

1. **Naming Convention**: Use descriptive, snake_case names for links
2. **Progressive Refinement**: Structure recipes as progressive refinement of information
3. **Schema Validation**: Define schemas for critical data points
4. **Reuse Templates**: Use templates to avoid repetition
5. **Keep It Simple**: Create focused recipes that do one thing well
6. **Document Assumptions**: Add comments to explain complex logic
7. **Version Your Recipes**: Update the version number when making significant changes
