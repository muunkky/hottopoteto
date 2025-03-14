# Eldorian Lexicon Schema Design

## Core Design Principles

- **Hierarchical Structure**: Base words serve as primary entries with derivatives referenced
- **Polymorphic Word Types**: Different parts of speech have specialized properties
- **Cross-Referential Relationships**: Words maintain semantic and etymological connections
- **Historical Preservation**: Etymology and evolution are tracked through language history
- **Metadata Enrichment**: Each entry includes generation context and schema version

## Relationship Types

### Morphological Relationships
Connections based on word formation rules:
- **derived_from**: Word created through affixation or other morphological process
- **compound_component**: Word that forms part of a compound
- **diminutive_of**: Smaller/lesser version of another word
- **augmentative_of**: Larger/greater version of another word

### Semantic Relationships
Connections based on meaning:
- **synonym**: Words with similar meanings (with optional strength indicator)
- **antonym**: Words with opposite meanings
- **hyponym**: More specific instance (e.g., "oak" is a hyponym of "tree")
- **hypernym**: More general category (e.g., "tree" is a hypernym of "oak")

### Etymological Relationships
Connections based on language history:
- **cognate**: Words with shared origins across languages
- **borrowed_from**: Words directly imported from another language
- **calque_of**: Word-for-word translation from another language

## Usage Guidelines

### Adding New Words
When adding a new word, consider:
1. Is it a base word or derivative?
2. What part of speech determines its grammatical properties?
3. What relationships should be established with existing words?

### Working with Grammatical Properties
Each part of speech has specialized properties:
- **Nouns**: Track gender, number, case
- **Verbs**: Include conjugation patterns, mood, tense, aspect
- **Adjectives**: Store comparison forms and agreement patterns

### Handling Homonyms
Words that share the same form but have different meanings:
1. Create separate entries with unique IDs
2. Cross-reference them in the "homonyms" array
3. Maintain separate etymologies and relationships