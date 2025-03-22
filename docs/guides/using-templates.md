# Using Templates in Hottopoteto

This guide explains how to work with templates in Hottopoteto to create reusable patterns and structured content.

## Template Types

Hottopoteto uses templates in two main categories:

### 1. Recipe Templates

Recipe templates are YAML/JSON files that define reusable patterns for recipes. They're stored in the `templates/recipes/` directory and can be referenced by other recipes.

### 2. Text Templates

Text templates are Jinja2 templates used primarily for structuring prompts to language models. They're stored in the `templates/text/` directory.

## Working with Text Templates

### Basic Text Templates

Text templates use Jinja2 syntax to define placeholders that are filled at runtime:

```jinja
# filepath: templates/text/greeting.txt
Hello {{ name }},

Thank you for using Hottopoteto. Today is {{ today }}.

{% if premium_user %}
You have access to premium features.
{% else %}
Consider upgrading to premium for additional features.
{% endif %}
```

### Using Text Templates in Recipes

To use a text template in a recipe, reference it in an LLM link:

```yaml
- name: "Generate_Greeting"
  type: "llm"
  template:
    file: "templates/text/greeting.txt"
    inputs:
      name: "{{ User_Input.data.name }}"
      today: "{{ now() | format_date }}"
      premium_user: "{{ User_Input.data.subscription_level == 'premium' }}"
```

### Template Variables

Templates can use variables from:

- Previous link outputs: `{{ Link_Name.data.field }}`
- Context variables: `{{ variable_name }}`
- Built-in functions: `{{ now() }}`, `{{ random_choice(['a', 'b', 'c']) }}`

### Template Filters

You can use filters to transform variable values:

```jinja
{{ text | upper }}                  # Convert to uppercase
{{ number | round(2) }}             # Round to 2 decimal places
{{ list | join(', ') }}             # Join list items with commas
{{ date | format_date('YYYY-MM-DD') }} # Format a date
```

## Working with Recipe Templates

### Creating Recipe Templates

Recipe templates are partial or complete recipes that can be reused:

```yaml
# filepath: templates/recipes/user_input_template.yaml
description: "Template for user input"
links:
  - name: "User_Input"
    type: "user_input"
    description: "Get user information"
    inputs:
      name:
        type: "string"
        description: "Your name"
      email:
        type: "string"
        description: "Your email"
        format: "email"
```

### Including Recipe Templates

Reference recipe templates in your recipes:

```yaml
name: "My Recipe"
description: "Recipe that uses a template"
version: "1.0"
includes:
  - template: "user_input_template.yaml"
    
links:
  - name: "Process_User"
    type: "function"
    function:
      name: "process_user_data"
    inputs:
      user_name: "{{ User_Input.data.name }}"
      user_email: "{{ User_Input.data.email }}"
```

### Extending Recipe Templates

You can also extend templates to add or override parts:

```yaml
name: "Extended Recipe"
description: "Recipe that extends a template"
version: "1.0"
extends: "base_recipe_template.yaml"

# Override description
links:
  # Add new links
  - name: "Additional_Step"
    type: "llm"
    prompt: "Process the data further"
```

## Template Organization

Organize templates in a structured way:

```
templates/
├── text/                  # Text templates
│   ├── common/            # Common templates
│   │   ├── header.txt
│   │   └── footer.txt
│   ├── emails/            # Email templates
│   │   ├── welcome.txt
│   │   └── notification.txt
│   └── prompts/           # LLM prompt templates
│       ├── story_prompt.txt
│       └── analysis_prompt.txt
└── recipes/               # Recipe templates
    ├── user_input.yaml
    ├── text_generation.yaml
    └── data_processing.yaml
```

## Best Practices

1. **Keep Templates Focused**: Each template should do one thing well
2. **Document Template Inputs**: Comment what variables are required
3. **Use Consistent Naming**: Follow a clear naming convention
4. **Organize Hierarchically**: Group related templates together
5. **Version Templates**: Consider versioning for important templates
6. **Test Templates**: Verify templates work with various inputs
7. **Share Common Components**: Extract repeated patterns into reusable templates

## Advanced Template Features

### Conditional Sections

```jinja
{% if condition %}
This text only appears if condition is true.
{% elif another_condition %}
This text appears if another_condition is true.
{% else %}
This is the fallback text.
{% endif %}
```

### Loops

```jinja
{% for item in items %}
- {{ item.name }}: {{ item.description }}
{% endfor %}
```

### Template Inheritance

For text templates, you can use Jinja2's inheritance:

```jinja
{% extends "base_template.txt" %}

{% block content %}
This replaces the content block in the base template.
{% endblock %}
```

Remember that text templates cannot reference other templates directly, while recipe templates can. This follows Hottopoteto's principle of template referencing.
