# Storage Domain

## Overview

The Storage domain provides data persistence capabilities for Hottopoteto recipes. It allows you to save, retrieve, query, and delete data using various storage adapters.

## Link Types

### storage.save

Save data to a collection with automatic template rendering.

**Template Rendering:** All Jinja2 template strings in your data are automatically rendered using the recipe execution context. This works recursively for nested dictionaries and lists.

**Schema:**
```yaml
- name: "Save Data"
  type: "storage.save"
  collection: "my_collection"     # Required: Collection name
  data:                           # Required: Data to save (templates auto-rendered)
    field1: "{{ LinkName.data.value }}"
    nested:
      field2: "{{ AnotherLink.data.nested.value }}"
    items:
      - "{{ Link.data.item1 }}"
      - "literal value"
  metadata:                       # Optional: Additional metadata
    source: "recipe"
    version: "1.0"
```

**Template Examples:**

```yaml
# Simple field reference
simple_field: "{{ MyLink.data.value }}"

# Nested data reference  
nested_field: "{{ MyLink.data.user.name }}"

# Using raw output
raw_field: "{{ MyLink.raw }}"

# Mixed with literal text
combined: "User {{ MyLink.data.name }} has {{ MyLink.data.count }} items"

# Lists with templates
items:
  - "{{ Link1.data.item }}"
  - "literal item"
  - "{{ Link2.data.another }}"

# Deeply nested structures
complex:
  level1:
    level2:
      value: "{{ Deep.data.value }}"
```

**Non-Template Values:**
- Numbers: `42`, `3.14`
- Booleans: `true`, `false`
- Null: `null`
- Strings without templates: `"literal string"`

All non-string and non-template values are preserved as-is.

**Output:**

Returns the saved entity with generated ID:
```python
{
  "raw": "...",
  "data": {
    "success": True,
    "message": "Entity saved successfully",
    "data": {
      "id": "my_collection-abc12345",
      "data": { ... },  # Your data with templates rendered
      "metadata": { ... },
      "timestamp": "2026-01-04T12:00:00"
    }
  }
}
```

### storage.get

Retrieve a specific entity by ID.

**Schema:**
```yaml
- name: "Get Data"
  type: "storage.get"
  collection: "my_collection"
  entity_id: "my_collection-abc12345"  # Or use template: "{{ SaveLink.data.data.id }}"
```

**Output:**
```python
{
  "success": True,
  "data": { ... }  # The retrieved entity
}
```

### storage.query

Query entities with optional filtering.

**Schema:**
```yaml
- name: "Query Data"
  type: "storage.query"
  collection: "my_collection"
  filter:                       # Optional: Filter criteria
    metadata.source: "recipe"
  limit: 10                     # Optional: Max results
  skip: 0                       # Optional: Skip results
```

**Output:**
```python
{
  "success": True,
  "results": [ ... ],  # Array of matching entities
  "count": 5
}
```

### storage.delete

Delete a specific entity.

**Schema:**
```yaml
- name: "Delete Data"
  type: "storage.delete"
  collection: "my_collection"
  entity_id: "my_collection-abc12345"
```

## Storage Adapters

### FileAdapter (Default)

Stores data as JSON files in `storage/data/<collection>/` directory.

**Configuration:**
```python
# Automatically used - no configuration needed
# Files saved to: storage/data/{collection}/{id}.json
```

**File Format:**
```json
{
  "id": "collection-abc12345",
  "data": { ... },
  "metadata": { ... },
  "timestamp": "2026-01-04T12:00:00"
}
```

## Template Rendering Details

### How It Works

When you use `storage.save`, the `_extract_data()` method recursively processes your data structure:

1. **Strings with templates** (`"{{ var }}"`) → Rendered using Jinja2
2. **Dictionaries** → Each value recursively rendered
3. **Lists** → Each item recursively rendered  
4. **Other types** → Preserved as-is (numbers, booleans, null)

### Template Context

Templates have access to all previous link outputs in the recipe:

```yaml
# Recipe context structure:
LinkName:
  data: { ... }  # Structured output
  raw: "..."     # Raw string output
```

### Helper Functions

Available in templates:
- `now()` - Returns current ISO timestamp

Example:
```yaml
data:
  created_at: "{{ now() }}"
  user: "{{ UserInput.data.name }}"
```

### Error Handling

- **Undefined variables**: Render as empty string (Jinja2 default)
- **Malformed templates**: Left as-is (e.g., `"{{ unclosed"`)
- **Template errors**: Logged and original string returned

## Examples

### Simple Data Save

```yaml
links:
  - name: "Get User Input"
    type: "user_input"
    prompt: "Enter your name"
    
  - name: "Save User"
    type: "storage.save"
    collection: "users"
    data:
      name: "{{ Get_User_Input.data }}"
      created: "{{ now() }}"
```

### Complex Nested Save

```yaml
links:
  - name: "Generate Word"
    type: "llm"
    prompt: "Create a word"
    
  - name: "Save Word Data"
    type: "storage.save"
    collection: "words"
    data:
      english_word: "{{ Generate_Word.data.english }}"
      conlang_word: "{{ Generate_Word.data.conlang }}"
      etymology:
        origin: "{{ Generate_Word.data.origin }}"
        components: "{{ Generate_Word.data.components }}"
      metadata:
        generated: "{{ now() }}"
        version: 1
```

### Query and Process

```yaml
links:
  - name: "Query Recent"
    type: "storage.query"
    collection: "words"
    limit: 10
    
  - name: "Process Results"
    type: "function"
    function: "lambda: len({{ Query_Recent.data.results }})"
```

## Best Practices

1. **Use descriptive collection names**: `"user_sessions"` not `"data"`
2. **Include metadata**: Add `source`, `version`, etc. for tracking
3. **Leverage templates**: Reference previous link outputs, don't duplicate
4. **Test template syntax**: Ensure `{{ }}` are balanced
5. **Handle undefined gracefully**: Use `{{ var | default('fallback') }}`

## Testing

Comprehensive unit tests in `tests/unit/test_storage_links.py` cover:
- Simple template rendering
- Nested dictionary templates
- List templates
- Non-string value preservation
- Undefined variable handling
- Malformed template handling

Run tests:
```bash
python -m pytest tests/unit/test_storage_links.py -v
```

## Troubleshooting

### Templates not rendering

**Symptom:** Saved data contains literal `"{{ }}"` strings

**Solution:** Ensure:
- Templates use correct syntax: `{{ LinkName.data.field }}`
- Link names match exactly (case-sensitive, spaces replaced with underscores)
- Referenced links executed before storage.save

### Undefined variables

**Symptom:** Empty strings in saved data

**Solution:**
- Check link name spelling in templates
- Verify data structure (use `.data` or `.raw` as appropriate)
- Add Jinja2 defaults: `{{ var | default('N/A') }}`

### Type preservation issues

**Symptom:** Numbers/booleans become strings

**Solution:**
- Don't wrap non-string values in templates
- Use: `number: 42` not `number: "{{ Link.data.count }}"`
- Only use templates for string values

## Architecture

### Class: StorageSaveLink

**Method: execute(link_config, context)**
- Entry point for storage.save links
- Calls `_extract_data()` to render templates
- Delegates to `save_entity()` function

**Method: _extract_data(data_source, context)**
- Recursive template renderer
- Handles dicts, lists, strings, primitives
- Preserves type information
- Logs warnings for errors

### Repository Pattern

Storage uses a repository pattern with pluggable adapters:
- `Repository` - High-level interface
- `StorageAdapter` - Base adapter class
- `FileAdapter` - JSON file storage

### Domain Functions

Registered functions:
- `save_entity(collection, data, metadata)` - Core save logic
- `get_entity(collection, entity_id)` - Core get logic
- `query_entities(collection, filter, limit, skip)` - Core query logic
- `delete_entity(collection, entity_id)` - Core delete logic

## Future Enhancements

Potential improvements:
- MongoDB adapter
- SQLite adapter  
- Redis adapter
- Schema validation
- Migration support
- Batch operations
- Transaction support
