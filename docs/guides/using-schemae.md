# Working with Schemas in Hottopoteto

This guide explains the different approaches to using schemas in Hottopoteto recipes and how to balance flexibility with structure.

## Schema Options in Recipes

Hottopoteto offers several ways to define and use schemas:

### 1. Schema References

Reference domain-registered schemas:

```yaml
- name: "Generate_Person"
  type: "llm"
  prompt: "Generate a person profile"
  output_schema: 
    $ref: "people.person"  # Reference to registered schema
```

### 2. Schema Extensions

Extend base schemas with custom fields:

```yaml
- name: "Generate_Person"
  type: "llm"
  prompt: "Generate a person"
  output_schema:
    base: "people.person"  # Base schema to extend
    properties:           # Additional properties
      favorite_color:
        type: "string"
    required: ["favorite_color"]  # Add to required fields
```

### 3. Inline Schemas

Define schemas directly in the recipe:

```yaml
- name: "Generate_Person"
  type: "llm"
  prompt: "Generate a person"
  output_schema:
    type: "object"
    properties:
      name: 
        type: "string"
      age:
        type: "integer"
    required: ["name", "age"]
```

### 4. Validation Against Models

Validate data against domain models:

```yaml
- name: "Generate_Person"
  type: "llm"
  prompt: "Generate a person"
  output_schema:
    type: "object"
    properties:
      name: 
        type: "string"
      age:
        type: "integer"
    required: ["name", "age"]
    _validate_against: "people.person"  # Optional validation
```

## Balancing Schema Flexibility and Structure

Different approaches offer different levels of flexibility:

1. **Full Schema Validation** - Most structured, least flexible
2. **Partial Schema Validation** - Balances structure and flexibility
3. **Schema References** - Reuse without repeating
4. **Schema Extensions** - Extend base schemas
5. **Free-form Data** - Most flexible, least structured

### Full Schema Validation

```yaml
output_schema:
  type: "object"
  properties:
    name:
      type: "string"
    age:
      type: "integer"
      minimum: 0
    email:
      type: "string"
      format: "email"
  required: ["name", "email"]
  additionalProperties: false  # Strict validation
```

**When to use**: When downstream links depend on specific fields being present and correctly formatted.

### Partial Schema Validation

```yaml
output_schema:
  type: "object"
  properties:
    name:
      type: "string"
    email:
      type: "string"
  required: ["name"]
  additionalProperties: true  # Allow extra properties
```

**When to use**: When you need certain key fields but want to allow flexibility for extra data.

### Free-form Data

Skip schema validation entirely for maximum flexibility:

```yaml
- name: "Generate_Content"
  type: "llm"
  prompt: "Generate creative content about any topic"
  # No output_schema defined
```

**When to use**: For exploratory work, creative content, or when structure isn't critical.

## Handling Schema Mismatches

When working with data that doesn't match your schema:

1. **Schema Coercion**: Use our `adapt_data_to_schema()` utility
2. **LLM-Powered Adaptation**: Have an LLM restructure the data
3. **Fallback Handling**: Define fallback paths when schemas don't match

## Best Practices

1. **Be explicit about requirements**: Clearly document required fields
2. **Document your schemas**: Include descriptions for all properties
3. **Use validation patterns**: Add formats, minimums, maximums, etc.
4. **Balance depth vs width**: Deep nesting makes schemas rigid
5. **Test with various inputs**: Ensure your schema works with real-world data
6. **Consider progressive validation**: Use more flexible schemas early, stricter schemas later

For more details, see the [Schema Reference](../reference/schemas.md) documentation.
