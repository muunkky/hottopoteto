# Domain System in LangChain V2

The domain system in LangChain V2 provides a mechanism for organizing functionality around specific subject areas or knowledge domains. This document explains how domains work and how to use them.

## What Are Domains?

Domains are specialized knowledge areas with their own:

- Data models and schemas
- Processing functions
- CLI commands
- Utilities specific to a subject area

Examples of domains include:
- Constructed languages (conlang)
- Storytelling
- Worldbuilding
- Data analysis

## Domain Architecture

The domain system consists of several components:

1. **Domain Interfaces**: Define the contract for each domain
2. **Domain Processors**: Implement domain-specific logic
3. **Domain Registry**: Central registry of available domains
4. **Domain Packages**: Packages that implement domain functionality

### Domain Interface

A domain interface defines the schema and capabilities a domain provides:

```python
{
  "name": "conlang",
  "version": "1.0.0",
  "schemas": [
    {
      "name": "word_schema",
      "schema": { ... }
    }
  ],
  "functions": [
    {
      "name": "create_grammatical_properties",
      "function": <function_reference>
    }
  ]
}
```

### Domain-Package Relationship

Domains and packages have a many-to-many relationship:

- A domain can be supported by multiple packages
- A package can support multiple domains

This allows for composability and specialization.

## Using Domains

### Listing Available Domains

```bash
python main.py domains list
```

### Getting Domain Information

```bash
python main.py domains info conlang
```

### Finding Packages for a Domain

```bash
python main.py domains packages conlang
```

### Using Domain-Specific Commands

```bash
python main.py words list --part-of-speech noun
```

## Implementing a Domain

To implement a domain:

1. **Create a domain directory**:
   ```
   domains/my_domain/
   ├── __init__.py           # Domain initialization
   ├── cli.py                # CLI commands
   ├── models.py             # Data models
   ├── processors.py         # Processing functions
   ├── schema.py             # Schema definitions
   └── migrations.py         # Schema migrations
   ```

2. **Create a domain processor**:
   ```python
   from .. import DomainProcessor, register_domain
   
   class MyDomainProcessor(DomainProcessor):
       """Processor for my_domain."""
       
       def __init__(self):
           """Initialize the processor."""
           self.repository = Repository(
               storage_dir=os.path.join("storage", "my_domain"),
               schema=get_my_schema(),
               domain="my_domain"
           )
       
       def get_schemas(self) -> List[str]:
           """Get the list of schemas supported by the domain."""
           return ["my_schema"]
           
       def get_functions(self) -> Dict[str, Any]:
           """Get domain-specific functions for the function registry."""
           return {
               "create_entry": self.create_entry,
               "update_entry": self.update_entry,
               # Domain-specific functions
               "my_function": self.my_function
           }
   
   # Register the domain
   register_domain("my_domain", MyDomainProcessor)
   ```

3. **Create domain-specific CLI commands**:
   ```python
   def register_commands(subparsers) -> None:
       """Register domain-specific commands."""
       # Register commands
       
   def handle_command(args) -> None:
       """Handle domain-specific commands."""
       # Handle command execution
   ```

## Domain Standards

Domains should provide:

1. **Standard Schemas**: Define the data structures
2. **Migration Paths**: For schema evolution
3. **CLI Commands**: For interacting with domain objects
4. **Utility Functions**: For domain-specific operations

## Best Practices

1. **Keep Domains Focused**: Each domain should have a clear purpose
2. **Document Schemas**: Clearly document data structures
3. **Support Migration**: Provide tools for schema migration
4. **Consider Compatibility**: Make domains work well with others

## Example: Conlang Domain

The conlang domain provides functionality for constructed languages:

```python
# Register the domain
class ConlangProcessor(DomainProcessor):
    # Implementation
    
register_domain("conlang", ConlangProcessor)

# Register schemas
register_domain_schema("conlang", "word_schema", WORD_SCHEMA)

# Register functions
register_domain_function("conlang", "create_grammatical_properties", 
                        create_grammatical_properties)
```

## Domain vs Package

While domains define a subject area, packages implement functionality. The key difference:

- **Domains**: Define what something is (e.g., "a word in a constructed language")
- **Packages**: Define what something does (e.g., "generates words using an LLM")

A domain might have multiple implementing packages, and a package might support multiple domains.
