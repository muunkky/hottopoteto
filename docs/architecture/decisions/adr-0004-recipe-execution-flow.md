# [ADR-0004] Recipe Execution Flow

## Status

Accepted

## Context

Recipes are the core mechanism for users to define and execute workflows in Hottopoteto. We needed to design a recipe execution system that:

- Processes recipes in a predictable sequence
- Manages data flow between links
- Handles errors gracefully
- Supports links from multiple domains
- Maintains execution context

## Decision

We have implemented a Recipe Execution Flow with the following components:

1. **RecipeExecutor**: Core class responsible for executing recipes, located in `core/executor.py`.

2. **Execution Process**:
   - Load recipe definition from YAML/JSON
   - Validate recipe structure and schemas
   - Create memory context for data sharing
   - Execute links in defined sequence
   - Pass data between links through memory context
   - Handle errors at link and recipe levels
   - Return final output

3. **Link Execution**: Each link is executed by:
   - Resolving its type through the registry
   - Preparing inputs from memory context
   - Executing the link's logic
   - Validating outputs against schemas
   - Storing results in memory context

4. **Memory Context**: A shared data structure that links can read from and write to during execution.

## Consequences

### Positive Consequences

- Clear, predictable execution flow for recipes
- Strong separation between recipe definition and execution
- Ability to combine links from different domains
- Consistent error handling
- Flexible data passing between links
- Support for schema validation at each step

### Negative Consequences

- Sequential execution limits parallelism
- Memory context can grow large with complex recipes
- Error in one link affects downstream execution
- Performance depends on individual link implementations

## Alternatives Considered

**Graph-Based Execution**: Using a directed acyclic graph (DAG) for recipe execution. Considered for future versions but deemed more complex than initially needed.

**Event-Driven Architecture**: Having links publish events that other links subscribe to. Rejected as less intuitive for recipe authors.

**Function Composition**: Using function composition rather than links. Rejected for being less flexible and harder to configure declaratively.

## Related Documents

- [Execution Flow](../../reference/architecture-map.md#execution-flow)
- [Architecture Overview - Recipes](../../concepts/architecture.md#recipes)
- [Architecture Overview - Executor](../../concepts/architecture.md#executor)
