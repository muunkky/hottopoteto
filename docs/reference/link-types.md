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

### LLM Extract to Schema Link

The `llm.extract_to_schema` link type extracts structured data from unstructured text using LLM with JSON mode. It auto-generates an intelligent extraction prompt from the target schema.

#### Required Parameters
- **type**: Must be "llm.extract_to_schema"
- **source**: Text to extract from (supports templates)
- **schema**: Target JSON Schema for extracted data

#### Optional Parameters
- **hint**: Extraction guidance for the LLM
- **model**: LLM model to use (default: "gpt-4o")
- **temperature**: Sampling temperature (default: 0.2 for accuracy)
- **provider**: LLM provider to use (default: "openai"; supports "anthropic")

#### Example
```yaml
- name: "Extract_Origins"
  type: "llm.extract_to_schema"
  source: "{{ Generate_Etymology.data.raw }}"
  schema: "{{ Working_Doc.data.schema.properties.origin_words }}"
  hint: "Focus on the fictional etymology components"
  model: "gpt-4o"
  temperature: 0.2
```

With inline schema:
```yaml
- name: "Extract_Person"
  type: "llm.extract_to_schema"
  source: "John Smith is 42 years old and works as an engineer."
  schema:
    type: "object"
    properties:
      name:
        type: "string"
      age:
        type: "integer"
      occupation:
        type: "string"
```

### LLM Enrich Link

The `llm.enrich` link type is a document-aware extraction that enriches an existing document with new information. Unlike `llm.extract_to_schema`, it sees the full document context including existing values, enabling smarter context-aware inference.

#### Required Parameters
- **type**: Must be "llm.enrich"
- **document**: Document to enrich (with schema and data)
- **source**: New information to incorporate

#### Optional Parameters
- **target_fields**: List of fields to populate, or "auto" for automatic detection
- **hint**: Enrichment guidance for the LLM
- **model**: LLM model to use (default: "gpt-4o")
- **temperature**: Sampling temperature (default: 0.3)
- **provider**: LLM provider to use (default: "openai"; supports "anthropic")

#### Example
```yaml
- name: "Enrich_Document"
  type: "llm.enrich"
  document: "{{ Working_Doc.data }}"
  source: "{{ Generate_Etymology.data.raw }}"
  target_fields:
    - "origin_words"
    - "revised_connotation"
  hint: "Extract the fictional etymologies"
```

With auto field detection:
```yaml
- name: "Auto_Enrich"
  type: "llm.enrich"
  document: "{{ Working_Doc.data }}"
  source: "{{ new_content }}"
  target_fields: "auto"
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

### Storage Init Link

The `storage.init` link type creates a "working document" for schema-driven workflows. It initializes a document with a schema definition and optional initial data, enabling downstream links to work with validated, structured data.

#### Required Parameters
- **type**: Must be "storage.init"
- **collection**: Storage collection name

#### Optional Parameters
- **schema**: JSON Schema definition (inline object or file reference)
- **initial_data**: Data to pre-populate document fields

#### Output Structure
The link returns a document reference with:
- **id**: Unique document ID
- **collection**: Storage collection name
- **schema**: The JSON Schema for validation
- **data**: Current document state (fields from schema with initial values or null)

#### Example
```yaml
- name: "Working_Doc"
  type: "storage.init"
  collection: "eldorian_words"
  schema:
    file: "schemas/eldorian_word.yaml"
  initial_data:
    english_word: "{{ User_Input.data.word }}"
    connotation: "{{ User_Input.data.connotation }}"
```

With inline schema:
```yaml
- name: "Working_Doc"
  type: "storage.init"
  collection: "recipes"
  schema:
    type: "object"
    properties:
      name:
        type: "string"
      ingredients:
        type: "array"
        items:
          type: "object"
          properties:
            item: { type: "string" }
            amount: { type: "string" }
  initial_data:
    name: "{{ Recipe_Name.data }}"
```

### Storage Update Link

The `storage.update` link type updates an existing document by merging new data while preserving existing fields. It validates the merged data against the document's schema.

#### Required Parameters
- **type**: Must be "storage.update"
- **document_id**: ID of the document to update (supports templates)
- **collection**: Storage collection name
- **data**: New data to merge into the document

#### Optional Parameters
- **merge**: If true (default), merge with existing data. If false, replace entirely.
- **array_merge**: How to handle arrays - "replace" (default) or "append"

#### Example
```yaml
- name: "Update_Origins"
  type: "storage.update"
  document_id: "{{ Working_Doc.data.id }}"
  collection: "{{ Working_Doc.data.collection }}"
  data:
    origin_words: "{{ Extract_Origins.data }}"
  merge: true
```

With array append:
```yaml
- name: "Add_Tags"
  type: "storage.update"
  document_id: "{{ doc.id }}"
  collection: "articles"
  data:
    tags: ["new-tag"]
  array_merge: "append"
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
