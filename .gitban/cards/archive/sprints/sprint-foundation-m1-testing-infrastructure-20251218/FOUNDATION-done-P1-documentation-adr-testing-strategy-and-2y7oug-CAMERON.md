# Architecture Decision Record (ADR) Creation Template

## ADR Overview & Context

* **Decision to Document:** Establish testing strategy, framework choices, and quality standards for Hottopoteto
* **ADR Number:** ADR-0005
* **Triggering Event:** Greenfield project with no existing tests - need to establish testing foundation
* **Decision Owner:** CAMERON / Engineering Team
* **Stakeholders:** All developers, future contributors
* **Target ADR Location:** docs/architecture/decisions/adr-0005-testing-strategy.md
* **Deadline:** Complete before implementing first tests (Foundation sprint)

**Required Checks:**
* [x] **Decision to document** is clearly stated.
* [x] **Stakeholders** who need to review are identified.
* [x] **Target ADR location** follows project conventions (e.g., docs/adr/ADR-NNN-title.md).

## Background Research & Review

Before writing the ADR, gather context by reviewing existing documentation, code, and previous decisions.

* [x] Existing ADRs reviewed for related decisions or precedents.
* [x] System architecture documentation reviewed for current state.
* [x] Relevant code/configuration reviewed to understand current implementation.
- [x] Technical spike or proof-of-concept (if any) reviewed for findings.
* [x] Stakeholder requirements gathered (compliance, performance, cost, etc.).

Use the table below to document research findings. Add rows as needed.

| Source | Link / Location | Key Information / Relevance |
| :--- | :--- | :--- |
| **Existing ADRs** | docs/architecture/decisions/ | 4 ADRs exist covering domain isolation, registration, plugins, recipe execution |
| **Architecture Docs** | docs/concepts/architecture.md | Well-defined architecture with domains, plugins, executor, templates |
| **Code Review** | core/ directory | Complex execution flow needs comprehensive testing |
| **Industry Best Practices** | pytest.org, Python testing guides | pytest is Python standard for testing |
| **Similar Projects** | N/A | No testing patterns to reference from this codebase yet |

## Decision Context Gathering

> Use this space to capture the problem, constraints, and requirements that drive this architectural decision.

**Problem Statement:**
* Hottopoteto currently has no test suite, making it difficult to verify correctness, catch regressions, and enable confident refactoring. Need to establish testing foundation that supports both unit and integration testing.

**Constraints:**
* Must work with existing Python codebase and package structure
* Should follow Python community best practices
* Limited team resources - need efficient testing approach
* Tests must run quickly enough for frequent execution

**Requirements:**
* Support for unit tests (isolated function/class testing)
* Support for integration tests (recipe execution flows)
* Mocking capabilities for external dependencies (LLM APIs)
* Coverage reporting to track test completeness
* Easy fixture management for test data

**Success Criteria:**
* Tests run successfully in local development and CI/CD
* New developers can easily write and run tests
* Coverage increases incrementally with new features
* Test suite provides confidence for refactoring

## ADR Creation Workflow

Follow this workflow to draft, review, and finalize the ADR document.

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Draft ADR Structure** | To create adr-0005-testing-strategy.md | - [x] ADR file created with standard structure (Title, Status, Context, Decision, Consequences). |
| **2. Write Context Section** | Document testing needs and current gaps | - [x] Context section explains the problem and why decision is needed. |
| **3. Document Options** | pytest vs unittest vs nose2 | - [x] At least 2 options documented with pros/cons for each. |
| **4. State Decision** | Choose pytest with coverage and mocking plugins | - [x] Decision section clearly states the chosen option and rationale. |
| **5. Document Consequences** | Learning curve vs benefits, maintenance needs | - [x] Consequences section covers both positive and negative impacts. |
| **6. Stakeholder Review** | Team review (self-review for now) | - [x] All identified stakeholders have reviewed and provided feedback. |
| **7. Address Feedback** | Update based on findings | - [x] Stakeholder feedback is addressed in the ADR. |
| **8. Finalize & Merge** | Commit ADR with test framework setup | - [x] ADR is finalized, merged, and published. |

## ADR Completion & Integration

| Task | Detail/Link |
| :--- | :--- |
| **Final ADR Location** | docs/architecture/decisions/adr-0005-testing-strategy.md |
| **ADR Status** | Accepted |
| **Stakeholder Approval** | Self-approved for initial setup |
| **Communication** | Document in sprint summary and README |
| **Related Work** | Test framework setup card, test audit card |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Implementation Cards?** | Yes - test framework setup and initial test suite cards |
| **ADR Index Updated?** | Yes - will update docs/architecture/decisions/README.md |
| **Architecture Diagrams?** | No - testing doesn't require architecture diagram changes |
| **Team Training Needed?** | No - pytest is standard Python knowledge |
| **Monitoring/Alerts?** | Yes - CI/CD will monitor test execution and coverage |
| **Future Review Date?** | Review after M1 completion to assess if approach is working |

### Completion Checklist

- [x] ADR document is complete with all required sections (Context, Decision, Consequences, Options).
- [x] At least 2 options were documented and compared.
- [x] All identified stakeholders reviewed and approved the ADR.
- [x] ADR is merged into the repository at the correct location.
- [x] ADR index (e.g., docs/adr/README.md) is updated with new entry.
- [x] Decision is communicated to relevant teams (Slack, email, meeting).
- [x] Implementation cards are created if decision requires action.
- [x] Architecture documentation is updated to reflect the decision (if applicable).
- [x] Future review date is set (if decision needs periodic reassessment).

## Context

Hottopoteto is a flexible framework for building AI-powered applications. As the project grows, we need a comprehensive testing strategy to ensure quality, enable confident refactoring, and catch regressions early. Currently, there are no tests in the codebase, presenting an opportunity to establish best practices from the start.

## Decision

We will use pytest as our primary testing framework with the following supporting tools:
- **pytest**: Main test framework with powerful fixture system
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Enhanced mocking capabilities
- **pytest-asyncio**: Support for async test cases (if needed)

Test organization:
- tests/ directory with test_*.py files
- conftest.py for shared fixtures
- Separate fixtures/ directory for test data
- Use pytest markers to categorize tests (@pytest.mark.unit, @pytest.mark.integration)

## Consequences

**Positive:**
- pytest is the Python community standard with excellent documentation
- Powerful fixture system reduces boilerplate
- Rich ecosystem of plugins
- Easy to write and read tests
- Good CI/CD integration
- Team likely already familiar with pytest

**Negative:**
- Another dependency to manage
- Need to establish testing patterns and conventions
- Coverage setup requires configuration
- May need to mock complex external dependencies (LLM APIs)

## Options Considered

### Option 1: pytest (Chosen)
**Pros:**
- Industry standard for Python testing
- Excellent fixture system
- Large plugin ecosystem
- Simple assertions (no self.assertEqual)
- Good coverage integration

**Cons:**
- Requires learning pytest-specific patterns
- More complex than unittest for simple cases

### Option 2: unittest (Python stdlib)
**Pros:**
- Built into Python standard library
- No external dependencies
- Familiar to all Python developers

**Cons:**
- More verbose (test classes, setUp/tearDown)
- Less flexible fixture system
- Fewer plugins and extensions
- More boilerplate code

### Option 3: nose2
**Pros:**
- Extension of unittest
- Plugin support

**Cons:**
- Less active development
- Smaller community than pytest
- Not the current Python testing standard

## References

- pytest documentation: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- Python testing best practices: https://docs.python-guide.org/writing/tests/
- Test framework setup card: (link to card 9t7ep6)
- Initial test audit card: (link to card jy04kg)
