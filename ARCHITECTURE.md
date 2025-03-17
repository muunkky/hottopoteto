# Hottopoteto Architecture

This document describes the high-level architecture of Hottopoteto, including key components and their relationships.

## System Overview

Hottopoteto uses a modular architecture with the following main components:

```mermaid
graph TD;
  Recipes --> Executor;
  Executor --> Links;
  Executor --> Domains;
  Domains --> Plugins;
  Plugins --> Storage;
```

---

## Core Components

### **Recipes**
Recipes are declarative **YAML** files that define a sequence of operations. They specify:

- **Links to execute**
- **Configuration** for each link
- **Input/output schemas**
- **Domain association** (optional)

#### **Example recipe structure:**
```yaml
name: "Example Recipe"
description: "Description of what this recipe does"
version: "1.0"
domain: "example_domain"
links:
  - name: "Link_1"
    type: "link_type"
    # link-specific configuration
  - name: "Link_2"
    type: "another_link_type"
    # link-specific configuration
```

---

### **Executor**
The **RecipeExecutor** processes recipes by:

- **Loading** the recipe definition
- **Executing each link** in sequence
- **Maintaining a memory context** for passing data between links
- **Handling errors and exceptions**
- **Returning the final output**

---

### **Links**
Links are the basic units of execution in recipes. Each link:

- Has a **specific type** (e.g., `llm`, `user_input`, `function`)
- Takes **inputs** from previous links or direct configuration
- Produces **outputs** that can be used by subsequent links
- Is **registered** by either the core system or plugins

---

### **Domains**
Domains represent specialized knowledge areas with their own models, schemas, and utilities. They provide:

- **Standard schemas** for domain-specific data
- **Processing functions** for domain objects
- **CLI commands** for domain operations
- **Domain-specific utilities**

---

### **Plugins**
Plugins extend functionality by adding new link types and other capabilities. Each plugin:

- Registers **one or more link types**
- Provides **schemas** for its link configurations
- May support **specific domains**
- Has its own **requirements and dependencies**

---

### **Storage**
The storage system provides persistence mechanisms through adapters:

- **File storage**
- **SQLite**
- **MongoDB**
- **Custom adapters**

---

## System Interactions

1. A recipe is loaded by the **RecipeExecutor**
2. The executor processes **each link** in sequence
3. Links may use **domain utilities** for specialized operations
4. Plugins provide additional **link types and capabilities**
5. Storage adapters persist **data when needed**

---

## Directory Structure

```
hottopoteto/
├── core/                  # Core system components
│   ├── domains.py         # Domain registry
│   ├── executor.py        # Recipe executor
│   ├── links/             # Link base classes
│   └── schemas/           # Schema registry
├── domains/               # Domain implementations
│   └── conlang/           # Example domain: constructed languages
├── plugins/               # Plugin implementations
│   ├── gemini/            # Google Gemini plugin
│   ├── mongodb/           # MongoDB plugin
│   └── sqlite/            # SQLite plugin
├── recipes/               # Recipe definitions
│   ├── examples/          # Example recipes
│   └── conlang/           # Domain-specific recipes
├── storage/               # Storage system
│   ├── adapters/          # Storage adapters
│   └── repository.py      # Repository interface
└── main.py                # Command-line interface
```

---

## Extension Points

Hottopoteto is designed to be extended through several mechanisms:

- **New Domains**: Create new domains by extending the domain system
- **New Plugins**: Create new plugins to add link types and capabilities
- **New Storage Adapters**: Create new storage adapters for different backends
- **Custom Link Types**: Register new link types for specialized tasks
- **Recipe Templates**: Create reusable recipe templates for common patterns

---

## Data Flow

1. **Input**: Recipe definition loaded from YAML/JSON
2. **Processing**: Links executed in sequence, with data passed through memory context
3. **Storage**: Results stored using the appropriate adapter
4. **Output**: Final results returned to the caller

---

## Error Handling

The system includes several levels of error handling:

- **Schema Validation**: Ensures input data conforms to schemas
- **Link Execution**: Catches and reports errors during link execution
- **Storage Operations**: Handles storage errors gracefully
- **CLI Interface**: Provides clear error messages to users

---

## Security Considerations

- **Code Execution**: Function links use a restricted execution environment
- **Data Validation**: Schema validation prevents malformed data
- **Resource Limits**: Controls for API usage and resource consumption
- **Error Messages**: Careful handling to prevent information leakage

