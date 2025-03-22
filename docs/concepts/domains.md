# Domain System in Hottopoteto

The domain system in Hottopoteto provides a mechanism for organizing functionality around specific subject areas or knowledge domains.

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
- LLM interactions
- Storage operations

## Domain Architecture

The domain system consists of several components:

1. **Domain Interfaces**: Define the contract for each domain
2. **Domain Functions**: Implement domain-specific logic
3. **Domain Registry**: Central registry of available domains
4. **Domain Schemas**: Standard data models for the domain
5. **Domain Packages**: Packages that implement domain functionality

### Domain Interface

A domain interface defines the schema and capabilities a domain provides:

```python
register_domain_interface("conlang", {
  "name": "conlang",
  "version": "1.0.0",
  "description": "Constructed language creation tools",
  "schemas": ["word", "phoneme", "morphology"],
  "functions": ["generate_words", "apply_sound_changes"]
})
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

## Domain Organization

Each domain follows a standard structure:

```
domains/domain_name/            # Domain root directory
├── __init__.py                 # Registration code
├── models.py                   # Data models and schemas
├── functions.py                # Domain-specific functions
├── utils.py                    # Utilities specific to this domain
├── links/                      # Domain-specific link handlers
│   └── __init__.py
├── cli/                        # CLI commands for this domain
│   └── __init__.py
├── schemas/                    # JSON schemas
│   └── __init__.py
└── README.md                   # Domain documentation
```

For complete details on domain organization, see [Creating Domains](../guides/creating-domains.md).

## Best Practices

1. **Standard Naming**: Use consistent naming for domain entities
2. **Schema Versioning**: Include version information in schemas
3. **Documentation**: Document domain interfaces clearly
4. **Validation**: Validate data against schemas
5. **Independence**: Keep domains independent from each other
