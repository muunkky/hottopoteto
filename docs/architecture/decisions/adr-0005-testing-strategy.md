# ADR-0005: Testing Strategy and Framework Selection

## Status

Accepted - 2025-12-18

## Context

Hottopoteto is a flexible framework for building AI-powered applications through composable recipes. As the project grows from its initial implementation phase, we need a comprehensive testing strategy to ensure quality, enable confident refactoring, and catch regressions early.

**Current State:**
- No existing test suite in the codebase
- Complex execution flow with recipe executor, domain system, and plugin architecture
- External dependencies (OpenAI, Anthropic, MongoDB, etc.) that need mocking
- Python-based project with standard package structure

**Testing Needs:**
- **Unit Testing**: Isolated testing of functions, classes, and modules (core/, plugins/)
- **Integration Testing**: End-to-end recipe execution flows
- **Fixture Management**: Reusable test data (sample recipes, domains, outputs)
- **Mocking**: External API calls (LLM providers, databases)
- **Coverage Tracking**: Measure test completeness and set quality gates
- **Developer Experience**: Easy to write, run, and debug tests locally and in CI/CD

**Constraints:**
- Must work with existing Python 3.12+ codebase
- Should follow Python community best practices
- Limited team resources - need efficient testing approach
- Tests must run quickly enough for frequent execution during development

## Decision

We will use **pytest** as our primary testing framework with the following supporting ecosystem:

### Core Framework
- **pytest 7.1+**: Main test framework with powerful fixture system
- **pytest-cov 3.0+**: Coverage reporting with HTML/XML/terminal output
- **pytest-mock 3.7+**: Enhanced mocking capabilities beyond unittest.mock
- **pytest-asyncio 0.18+**: Support for async test cases (future-proofing)

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── unit/                    # Fast, isolated unit tests
│   ├── test_executor.py
│   ├── test_registry.py
│   └── test_domains.py
├── integration/             # End-to-end integration tests
│   ├── test_recipe_execution.py
│   └── test_plugin_system.py
└── fixtures/                # Test data (sample YAMLs, mock outputs)
    ├── recipes/
    └── outputs/
```

### Configuration
- **pytest.ini**: Test discovery, markers, coverage settings
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Coverage Target**: Start with 50% baseline, grow to 80%+ over time
- **Coverage Scope**: `core/` and `plugins/` directories

### Testing Patterns
1. **Fixture-Based Setup**: Use conftest.py for reusable test data and mocks
2. **Parametrized Tests**: Test multiple inputs with `@pytest.mark.parametrize`
3. **Mock External Dependencies**: Mock LLM APIs, database connections
4. **Test Discovery**: Follow pytest conventions (test_*.py files, test_* functions)

## Consequences

### Positive
- **Industry Standard**: pytest is the de facto Python testing framework with excellent documentation
- **Powerful Fixtures**: Reduces boilerplate, enables complex test setups
- **Rich Ecosystem**: 800+ plugins for extensions (coverage, mocking, profiling, etc.)
- **Simple Assertions**: No `self.assertEqual` - just `assert x == y`
- **Easy CI/CD Integration**: Works seamlessly with GitHub Actions, Jenkins, GitLab CI
- **Team Familiarity**: Most Python developers already know pytest
- **Incremental Adoption**: Can start small and grow test suite over time

### Negative
- **Additional Dependency**: One more package to manage (though minimal overhead)
- **Learning Curve**: Pytest-specific patterns (fixtures, markers) for new contributors
- **Configuration Complexity**: Initial setup of conftest.py and pytest.ini
- **Mock Management**: Complex mocking for external APIs (OpenAI, MongoDB) requires discipline

### Mitigations
- **Documentation**: Add comprehensive testing section to README.md
- **Examples**: Provide well-documented test examples in initial test suite
- **Templates**: Create test templates for common patterns (recipe tests, domain tests)
- **Review**: Code review process ensures test quality and coverage

## Options Considered

### Option 1: pytest (Chosen) ✅

**Description**: Use pytest as the primary testing framework with coverage and mocking plugins.

**Pros:**
- Industry standard for Python testing (used by 80%+ of Python projects)
- Excellent fixture system for dependency injection and test isolation
- Large plugin ecosystem (pytest-cov, pytest-mock, pytest-asyncio, pytest-xdist)
- Simple, readable assertions (`assert x == y` vs `self.assertEqual(x, y)`)
- Good coverage integration with multiple report formats
- Powerful parametrization for testing multiple inputs
- Active development and community support

**Cons:**
- Requires learning pytest-specific patterns (fixtures, markers)
- More complex than unittest for trivial cases
- Plugin management adds slight overhead

**Verdict**: Best choice for modern Python projects prioritizing developer experience and maintainability.

---

### Option 2: unittest (Python Standard Library)

**Description**: Use Python's built-in unittest framework with manual coverage setup.

**Pros:**
- Built into Python standard library (no external dependencies)
- Familiar to all Python developers (taught in tutorials)
- No version conflicts or dependency management
- Simple for basic test cases

**Cons:**
- More verbose (test classes, setUp/tearDown methods)
- Less flexible fixture system compared to pytest
- Fewer plugins and extensions available
- More boilerplate code (`self.assertEqual`, `self.assertTrue`, etc.)
- Coverage requires separate setup (coverage.py)
- Less modern than pytest

**Verdict**: Rejected - Too much boilerplate for complex test scenarios. pytest is the modern standard.

---

### Option 3: nose2 / nose

**Description**: Extension of unittest with plugin support.

**Pros:**
- Extension of unittest with better features
- Some plugin support available
- Compatible with existing unittest tests

**Cons:**
- **nose is deprecated** (development stopped in 2015)
- nose2 has much smaller community than pytest
- Not the current Python testing standard
- Fewer plugins than pytest ecosystem
- Less active development

**Verdict**: Rejected - Not recommended for new projects. pytest has eclipsed nose/nose2.

## Implementation Plan

1. ✅ **Install Dependencies** (Completed)
   - Added pytest, pytest-cov, pytest-mock, pytest-asyncio to requirements.txt
   - Installed in virtual environment

2. ✅ **Configure pytest** (Completed)
   - Created pytest.ini with test discovery, markers, coverage settings
   - Configured coverage for core/ and plugins/ directories

3. ✅ **Create Test Infrastructure** (Completed)
   - Created tests/conftest.py with shared fixtures
   - Set up tests/unit/ and tests/integration/ directories
   - Added initial test files (test_executor.py, test_registry.py, test_domains.py)

4. ✅ **Document Testing Process** (Completed)
   - Added Testing section to README.md
   - Included instructions for running tests, coverage reports

5. ⏭️ **Establish Test Baseline** (Next Card)
   - Audit existing code for test coverage opportunities
   - Create initial unit tests for critical paths
   - Set coverage baseline and quality gates

6. ⏭️ **CI/CD Integration** (Future)
   - Add pytest to GitHub Actions workflow
   - Enforce coverage thresholds in CI
   - Generate coverage badges

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test Pyramid Concept](https://martinfowler.com/articles/practical-test-pyramid.html)
- Test Framework Setup: Card 9t7ep6
- Initial Test Baseline: Card jy04kg

## Review History

- **2025-12-18**: Initial ADR created by CAMERON
- **Status**: Accepted - Framework implemented and validated
