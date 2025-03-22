# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Hottopoteto project.

## What is an Architecture Decision Record?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

## ADR Contents

Each ADR describes:
- The architectural decision
- The context in which it was made
- The consequences of the decision
- Alternatives that were considered

## List of ADRs

| Number | Title | Status |
|--------|-------|--------|
| [ADR-0001](./adr-0001-domain-isolation-pattern.md) | Domain Isolation Pattern | Accepted |
| [ADR-0002](./adr-0002-domain-registration-system.md) | Domain Registration System | Accepted |
| [ADR-0003](./adr-0003-plugin-discovery-mechanism.md) | Plugin Discovery Mechanism | Accepted |
| [ADR-0004](./adr-0004-recipe-execution-flow.md) | Recipe Execution Flow | Accepted |

## Creating New ADRs

1. Copy the [ADR template](./adr-template.md) to create a new ADR
2. Name it using the pattern `adr-NNNN-title.md` where `NNNN` is the next number in sequence
3. Fill in the template with your architectural decision
4. Update this README.md to include your new ADR in the list
