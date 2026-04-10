# Schema Templates

This directory contains JSON Schema files that define the structure of documents
built by recipes using the schema-driven document enrichment pattern.

## Usage

Reference schemas in recipe configs using the `file:` pattern:

```yaml
- name: "Working_Doc"
  type: "storage.init"
  schema:
    file: "conlang/eldorian_word.yaml"
```

## Directory Structure

```
schemas/
├── README.md
├── conlang/
│   └── eldorian_word.yaml
└── examples/
    └── simple_document.yaml
```

## Schema Format

Schemas use JSON Schema format but can be written in YAML for readability:

```yaml
type: object
properties:
  name:
    type: string
    description: The name of the item
  count:
    type: integer
    minimum: 0
required:
  - name
```

## See Also

- [ADR-0006: Schema-Driven Document Enrichment](../../docs/architecture/decisions/adr-0006-schema-driven-document-enrichment.md)
- [Recipe Format Reference](../../docs/reference/recipe-format.md)
