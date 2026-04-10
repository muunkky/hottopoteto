# [ADR-0006] Schema-Driven Document Enrichment

## Status

Proposed

## Context

During development, we discovered that the `master_output_schema` feature documented in `docs/reference/recipe-format.md` was never actually implemented. This "ghost feature" highlighted a fundamental gap in our architecture: **recipes have no mechanism to progressively build structured, validated documents**.

### Current State Problems

1. **Ghost Feature**: `master_output_schema` is documented but not implemented. Recipe authors expect it to work but it's completely ignored by the executor.

2. **Unstructured Output**: LLM links return prose text that gets passed directly to `storage.save`. The original structured intent (defined in complex 165-line schemas like `eldorian_word.yaml`) is lost.

3. **No Progressive Building**: Recipes cannot incrementally build documents across multiple LLM calls with validation at each step.

4. **Domain Isolation Conflict**: Per ADR-0004, recipes execute for side effects, not return values. Any solution must respect this philosophy and the domain isolation principle from ADR-0001.

### Triggering Event

A user investigation into why recipe output "doesn't make sense and isn't the schema from the recipe" revealed the ghost feature and exposed the architectural gap.

## Decision

We will implement a **two-step LLM+Storage architecture** that preserves domain isolation while enabling structured document building:

### New Link Types

1. **`storage.init`** - Creates a "working document" with a schema
   - Loads schema from external file (like prompt templates)
   - Initializes document with provided values, nulls for rest
   - Returns document ID, schema, and current state

2. **`storage.update`** - Merges data into existing document
   - References document by ID from `storage.init`
   - Deep merges new data with existing document
   - Validates against stored schema
   - Returns updated document state

3. **`llm.extract_to_schema`** - Extracts structured data from text
   - Takes source text + target schema
   - Auto-generates extraction prompt from schema
   - Uses LLM JSON mode for reliable output
   - Returns data matching schema structure

4. **`llm.enrich`** - Document-aware extraction
   - Sees full document context (existing fields)
   - Extracts and populates specified target fields
   - Makes smarter inferences with full context
   - Returns complete enriched document

### External Schema Files

Schemas will be stored in `templates/schemas/` directory, following the existing pattern for prompt templates in `templates/text/`. This keeps configuration external and maintainable.

### Data Flow Pattern

```yaml
# Example recipe pattern
- name: "Working_Doc"
  type: "storage.init"
  schema: { file: "schemas/eldorian_word.yaml" }
  initial_data:
    english_word: "{{ user_input }}"

- name: "Generate_Origins"
  type: "llm"
  prompt: { file: "prompts/generate_origins.md" }

- name: "Enrich_Origins"
  type: "llm.enrich"
  document: "{{ Working_Doc.data }}"
  source: "{{ Generate_Origins.data.raw }}"
  target_fields: ["origin_words"]

- name: "Save_Origins"
  type: "storage.update"
  document_id: "{{ Working_Doc.data.id }}"
  data: "{{ Enrich_Origins.data }}"
```

### Why This Architecture

The key insight is **separation of concerns**:
- **LLM domain** is responsible for extraction and enrichment (transforming text to structured data)
- **Storage domain** is responsible for persistence and validation (maintaining document integrity)

Domains communicate via the shared memory context, not direct calls, preserving isolation.

## Consequences

### Positive Consequences

- **Structured Output**: Recipes can now produce validated, structured documents
- **Progressive Building**: Documents can be built incrementally across multiple LLM calls
- **Domain Isolation Preserved**: LLM and storage domains remain independent
- **Backward Compatible**: Existing recipes continue to work unchanged
- **Consistent Pattern**: External schema files follow existing template file pattern
- **Better DX**: Clear separation makes recipes easier to understand and debug

### Negative Consequences

- **More Verbose Recipes**: Simple cases require more links than before
- **New Concepts to Learn**: Recipe authors need to understand init/update/enrich pattern
- **Schema Duplication Risk**: Same schema might be defined in multiple places
- **Performance Overhead**: Additional LLM calls for extraction/enrichment

### Mitigations

- Provide helper templates and examples for common patterns
- Document the pattern thoroughly in recipe-format.md
- Consider schema $ref support for deduplication in future
- Optimize LLM calls with caching where possible

## Alternatives Considered

### Option 1: Smart Storage (Rejected)

Have `storage.save` automatically detect when LLM output doesn't match schema and call the LLM to fix it.

**Rejected because**: Violates domain isolation. Storage domain should not call LLM domain.

### Option 2: New Document Domain (Rejected)

Create a dedicated `document` domain that orchestrates LLM and storage.

**Rejected because**: Adds complexity without benefit. The two-step pattern achieves the same result with existing domains.

### Option 3: Implement master_output_schema (Rejected)

Actually implement the documented `master_output_schema` feature for final validation.

**Rejected because**: Doesn't solve progressive building. Post-hoc validation can't fix malformed data, only reject it.

## Implementation Plan

1. **Step 1**: Create this ADR (documentation)
2. **Step 2**: Implement external schema file loading
3. **Step 3**: Implement `storage.init` link type
4. **Step 4**: Implement `storage.update` link type
5. **Step 5**: Implement `llm.extract_to_schema` link type
6. **Step 6**: Implement `llm.enrich` link type
7. **Step 7**: Sprint closeout with documentation and examples

See DOCENRICH sprint cards for detailed implementation plans.

## Related Documents

- [ADR-0001: Domain Isolation Pattern](adr-0001-domain-isolation-pattern.md)
- [ADR-0004: Recipe Execution Flow](adr-0004-recipe-execution-flow.md)
- [Recipe Format Reference](../../reference/recipe-format.md)
- [Architecture Principles](../../concepts/principles.md)
