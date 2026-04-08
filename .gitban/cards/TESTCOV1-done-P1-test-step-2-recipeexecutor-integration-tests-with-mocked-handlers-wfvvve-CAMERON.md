# Test Implementation Card

**When to use this template:** Use this when you need to add, improve, or verify test coverage for any part of the system - whether unit tests, integration tests, E2E tests, or performance benchmarks.

---

## Test Overview

**Test Type:** Integration

**Target Component:** RecipeExecutor (`core/executor.py`)

**Related Cards:** TESTCOV1 sprint — testing infrastructure coverage gate

**Coverage Goal:** 16 integration tests covering executor dispatch, handler mocking, link chaining, error propagation, and recipe-level orchestration

---

## Test Strategy

### Test Pyramid Placement

| Layer | Tests Planned | Rationale |
|-------|---------------|-----------|
| Unit | N/A | Covered in separate unit cards |
| Integration | 16 | Verify executor orchestrates handlers correctly with mocked I/O |
| E2E | N/A | Out of scope for this card |
| Performance | N/A | Out of scope for this card |

### Testing Approach
- **Framework:** pytest
- **Mocking Strategy:** Mock individual link handlers (LLM, storage) at the handler registration boundary; real executor dispatch path exercised
- **Isolation Level:** Full isolation — no real LLM or storage calls

---

## Test Scenarios

### Scenario 1: Happy Path — Single Link Recipe Executes Successfully
- **Given:** A recipe with one link and a mocked handler registered
- **When:** Executor runs the recipe
- **Then:** Handler is called once, output context contains expected result
- **Priority:** Critical

### Scenario 2: Chained Links — Output of Link N Feeds Link N+1
- **Given:** A recipe with two links, second depends on first's output
- **When:** Executor runs the recipe
- **Then:** Context is threaded correctly between links
- **Priority:** Critical

### Scenario 3: Handler Raises — Error Propagates Cleanly
- **Given:** A mocked handler that raises an exception
- **When:** Executor runs the recipe
- **Then:** Exception propagates with clear context; no silent swallow
- **Priority:** High

### Scenario 4: Unknown Link Type — Raises Descriptive Error
- **Given:** A recipe referencing a link type with no registered handler
- **When:** Executor runs the recipe
- **Then:** Raises a descriptive error naming the unknown type
- **Priority:** High

---

## Test Data & Fixtures

### Required Test Data
| Data Type | Description | Source |
|-----------|-------------|--------|
| Recipe dict | Minimal in-memory recipe with 1–3 links | Inline fixture |
| Mock handler | Callable returning controlled output | `unittest.mock.MagicMock` |

### Edge Case Data
- **Empty/Null:** Recipe with zero links — verify no-op success
- **Maximum Values:** N/A for integration scope
- **Invalid Formats:** Recipe missing required keys — verify early validation error
- **Unicode/Special Chars:** N/A

### Fixture Setup
```python
# Minimal recipe fixture
def make_recipe(*links):
    return {"links": list(links)}

def make_link(link_type, **kwargs):
    return {"type": link_type, **kwargs}
```

---

## Implementation Checklist

### Setup Phase
- [x] Test file[s] created in correct location
- [x] Test fixtures/factories defined
- [x] Mocks and stubs configured
- [x] Test database/state initialized [if needed]

### Test Implementation
- [x] Happy path tests written and passing
- [x] Edge case tests written and passing
- [x] Error handling tests written and passing
- [x] Negative/security tests written and passing
- [x] Performance assertions added [if applicable]

### Quality Gates
- [x] All tests pass locally
- [x] All tests pass in CI
- [x] No flaky tests introduced
- [x] Test execution time acceptable
- [x] Code coverage meets target [if applicable]

### Documentation
- [x] Test file has clear docstrings/comments
- [x] Complex test logic explained
- [x] Setup/teardown documented

---

## Acceptance Criteria

- [x] All planned scenarios have corresponding tests
- [x] Tests are deterministic [no flakiness]
- [x] Tests run in isolation [no order dependency]
- [x] Tests are fast enough for CI [<X seconds]
- [x] Coverage target met: 16 integration tests passing
- [x] Tests follow project conventions

---

## Notes

Test file: `tests/integration/test_executor_integration.py`
16 tests written and passing. Mocked handlers via unittest.mock. Covers dispatch, chaining, error propagation, and unknown-type handling. Part of TESTCOV1 sprint testing infrastructure work.
