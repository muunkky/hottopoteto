# Templates in Hottopoteto

Hottopoteto uses templates in two main categories:

## Recipe Templates

Recipe templates (`templates/recipes/`) are YAML/JSON files that define a sequence of operations (links) to execute. They're the primary way to automate tasks in Hottopoteto.

```yaml
name: "Example Recipe"
description: "Example recipe demonstrating text generation"
links:
  - name: "Generate_Text"
    type: "llm"
    prompt: "Generate a {{subject}} for me."
    # ...configuration...
```

## Text Templates

Text templates (`templates/text/`) are Jinja2 templates used primarily for structuring prompts to language models. They can reference variables from context or other templates.

