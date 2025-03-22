# Schema Formats Reference

This document provides a comprehensive reference for schema formats used in Hottopoteto.

## Overview

Schemas in Hottopoteto are based on JSON Schema and are used to:

1. Validate data structures
2. Generate forms for user input
3. Structure LLM outputs
4. Document data models

## Basic Schema Structure

A basic schema includes:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "The user's name"
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 120
    }
  },
  "required": ["name"]
}
```

## Data Types

Hottopoteto supports the following JSON Schema data types:

### Primitive Types

- `string`: Text values
- `integer`: Whole numbers
- `number`: Any numeric value (including decimals)
- `boolean`: True or false values
- `null`: Null value

### Complex Types

- `object`: Collection of key-value pairs
- `array`: Ordered list of values

## Schema Extensions

Hottopoteto extends the standard JSON Schema format with some custom features:

### Domain References

Reference schemas defined in domains:

```json
{
  "$ref": "domain_name.schema_name"
}
```

### Schema Extensions

Extend an existing schema:

```json
{
  "base": "domain_name.schema_name",
  "properties": {
    "additional_property": {
      "type": "string"
    }
  }
}
```

### Validation Hints

Provide hints for validation:

```json
{
  "_validate_against": "domain_name.schema_name",
  "_transform": "function_name"
}
```

## Common Patterns

### String Format Validation

```json
{
  "type": "string",
  "format": "email"  // or: date-time, uri, uuid, etc.
}
```

### Numeric Constraints

```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 100,
  "multipleOf": 5
}
```

### String Constraints

```json
{
  "type": "string",
  "minLength": 8,
  "maxLength": 50,
  "pattern": "^[A-Za-z0-9]+$"  // Regular expression
}
```

### Arrays

```json
{
  "type": "array",
  "items": {
    "type": "string"
  },
  "minItems": 1,
  "maxItems": 10,
  "uniqueItems": true
}
```

### Enumerations

```json
{
  "type": "string",
  "enum": ["option1", "option2", "option3"],
  "default": "option1"
}
```

### Conditional Fields

```json
{
  "type": "object",
  "properties": {
    "payment_type": {
      "type": "string",
      "enum": ["credit_card", "bank_transfer"]
    },
    "card_number": {
      "type": "string"
    }
  },
  "required": ["payment_type"],
  "if": {
    "properties": {
      "payment_type": { "enum": ["credit_card"] }
    }
  },
  "then": {
    "required": ["card_number"]
  }
}
```

## Schema Registration

Domains can register schemas using the `register_domain_schema` function:

```python
register_domain_schema(
    domain_name="my_domain",
    schema_name="my_schema",
    schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        }
    }
)
```

## Schema Resolution

When Hottopoteto encounters a schema reference like `domain_name.schema_name`, it:

1. Looks up the schema in the domain registry
2. Resolves any nested references
3. Validates the schema
4. Uses it for validation or generation

## Forms Generation

Schemas can be used to automatically generate user input forms:

```yaml
- name: "User_Info"
  type: "user_input"
  inputs:
    user_profile:
      $ref: "users.profile"
```

## Best Practices

1. **Use descriptive property names**: Choose clear, readable names
2. **Add descriptions**: Include descriptions for properties
3. **Be specific with types**: Use specific data types and constraints
4. **Version your schemas**: Include version information in schemas
5. **Keep schemas focused**: Create specific schemas for specific purposes
6. **Document required fields**: Clearly indicate required fields
7. **Use standard formats**: Use standard formats for common data types
8. **Consistent naming**: Follow a consistent naming convention
