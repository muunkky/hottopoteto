# Link Types Reference

This document provides a comprehensive reference for all link types available in Hottopoteto.

## Core Link Types

### LLM Link

The `llm` link type sends prompts to language models and captures their responses.

#### Required Parameters
- **type**: Must be "llm"
- **prompt** OR **template**: Text to send to the LLM

#### Optional Parameters
- **model**: Model to use (default: "gpt-4o")
- **temperature**: Sampling temperature (default: 0.7)
- **token_limit**: Maximum tokens to generate (default: 512)
- **output_schema**: Schema for structured output
- **conversation**: Conversation mode ("none", "default", or custom ID)

#### Example
```yaml
- name: "Generate_Text"
  type: "llm"
  model: "gpt-4o"
  prompt: "Write a short poem about {{subject}}."
  temperature: 0.7
  output_schema:
    properties:
      poem:
        type: "string"
    required: ["poem"]
```

### User Input Link

The `user_input` link type collects input from the user.

#### Required Parameters
- **type**: Must be "user_input"
- **inputs**: Map of input fields to collect

#### Optional Parameters
- **description**: Description shown to the user
- **timeout**: Timeout in seconds (default: none)
- **output_schema**: Schema for structured output

#### Example
```yaml
- name: "Get_User_Input"
  type: "user_input"
  description: "Please provide the following information:"
  inputs:
    name:
      type: "string"
      description: "Your name"
      required: true
    age:
      type: "integer"
      description: "Your age"
      min: 0
      max: 120
    interests:
      type: "array"
      description: "Your interests"
      items:
        type: "string"
```

### Function Link

The `function` link type executes code or predefined functions.

#### Required Parameters
- **type**: Must be "function"
- **function**: Function configuration

#### Function Configuration Options
- **name**: Name of a registered function
- **code**: Direct code to execute (Python or JavaScript)
- **language**: Code language (default: "python")

#### Example
```yaml
- name: "Calculate_Stats"
  type: "function"
  function:
    name: "calculate_metrics"
  inputs:
    data: "{{ previous_link.data.results }}"
```

Or with direct code:

```yaml
- name: "Calculate_Stats"
  type: "function"
  function:
    code: "return {'sum': sum(inputs['values']), 'avg': sum(inputs['values'])/len(inputs['values'])}"
    language: "python"
  inputs:
    values: "{{ previous_link.data.numbers }}"
```

## Storage Links

### Storage Save Link

The `storage.save` link type saves data to persistent storage.

#### Required Parameters
- **type**: Must be "storage.save"
- **collection**: Storage collection name
- **data**: Data object or reference to save

#### Optional Parameters
- **id**: Custom ID for the entity (auto-generated if not provided)
- **metadata**: Additional metadata for the entity

#### Example
```yaml
- name: "Save_Content"
  type: "storage.save"
  collection: "articles"
  data: "{{ Generate_Article.data }}"
  metadata:
    created_at: "{{ now() }}"
    source: "auto-generated"
```

### Storage Get Link

The `storage.get` link type retrieves data from storage.

#### Required Parameters
- **type**: Must be "storage.get"
- **collection**: Storage collection name
- **id**: Entity ID to retrieve

#### Example
```yaml
- name: "Get_Article"
  type: "storage.get"
  collection: "articles"
  id: "{{ article_id }}"
```

### Storage Query Link

The `storage.query` link type searches for data in storage.

#### Required Parameters
- **type**: Must be "storage.query"
- **collection**: Storage collection name

#### Optional Parameters
- **filter**: Filter criteria (field/value pairs)
- **limit**: Maximum number of results
- **skip**: Number of results to skip

#### Example
```yaml
- name: "Find_Articles"
  type: "storage.query"
  collection: "articles"
  filter:
    author: "{{ current_user }}"
    published: true
  limit: 10
```

### Storage Delete Link

The `storage.delete` link type removes data from storage.

#### Required Parameters
- **type**: Must be "storage.delete"
- **collection**: Storage collection name
- **id**: Entity ID to delete (or array of IDs)

#### Example
```yaml
- name: "Delete_Article"
  type: "storage.delete"
  collection: "articles"
  id: "{{ article_id }}"
```

## Utility Links

### Log Link

The `log` link type writes messages to the log.

#### Required Parameters
- **type**: Must be "log"
- **message**: Message to log

#### Optional Parameters
- **level**: Log level (default: "info")

#### Example
```yaml
- name: "Log_Step"
  type: "log"
  level: "info"
  message: "Processing data for {{ User_Input.data.name }}"
```

### File Link

The `file` link type reads or writes files.

#### Required Parameters
- **type**: Must be "file"
- **operation**: "read" or "write"
- **path**: File path

#### Optional Parameters
- **content**: Content to write (for "write" operation)
- **format**: Format for reading/writing ("text", "json", "yaml", "binary")

#### Example
```yaml
- name: "Write_Result"
  type: "file"
  operation: "write"
  path: "output/result.json"
  content: "{{ Generate_Content.data }}"
  format: "json"
```

### HTTP Link

The `http` link type makes HTTP requests.

#### Required Parameters
- **type**: Must be "http"
- **url**: URL to request
- **method**: HTTP method (GET, POST, PUT, DELETE, etc.)

#### Optional Parameters
- **headers**: Request headers
- **data**: Request body data
- **params**: URL query parameters

#### Example
```yaml
- name: "Fetch_Data"
  type: "http"
  url: "https://api.example.com/data"
  method: "GET"
  headers:
    Authorization: "Bearer {{ env('API_KEY') }}"
  params:
    query: "{{ User_Input.data.search_term }}"
```

## Plugin-Provided Link Types

These link types are provided by plugins that must be installed separately.

### Gemini Link

The `gemini` link type uses Google's Gemini models.

#### Required Parameters
- **type**: Must be "gemini"
- **prompt** OR **template**: Text to send to the model

#### Optional Parameters
- Similar to `llm` link type

#### Example
```yaml
- name: "Generate_With_Gemini"
  type: "gemini"
  model: "gemini-1.5-pro-latest"
  prompt: "Generate a creative story about {{ theme }}"
```

### MongoDB Link

The `mongodb` link provides direct access to MongoDB.

#### Required Parameters
- **type**: Must be "mongodb"
- **operation**: MongoDB operation
- **collection**: Collection name

#### Example
```yaml
- name: "Find_Documents"
  type: "mongodb"
  operation: "find"
  collection: "users"
  filter:
    active: true
  projection:
    name: 1
    email: 1
    _id: 0
```

## Custom Link Types

You can register custom link types through plugins. For details, see the [Creating Plugins](../guides/creating-plugins.md) guide.
