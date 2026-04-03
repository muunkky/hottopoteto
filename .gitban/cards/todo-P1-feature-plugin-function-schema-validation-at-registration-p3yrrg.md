# Plugin Function Schema Validation at Registration

**When this feature is needed:** Plugin authors can currently register functions with incomplete or invalid schemas, causing runtime errors only when recipes attempt to use them. Function schemas should be validated during plugin registration as a quality gate, catching authoring errors immediately before any recipes are affected.

## Feature Overview & Context

* **Associated Ticket/Epic:** Follow-up to Card oroau2 (Pre-Execution Recipe Template Validation) - completing the validation architecture
* **Feature Area/Component:** Plugin Registration System (core/registration/)
* **Target Release/Milestone:** Next minor version (completes fail-fast validation architecture alongside ADR-016)

**Problem Statement:**
Current plugin registration accepts function definitions without validating their schemas. This means:
- Missing required parameter definitions aren't caught until recipe execution
- Invalid parameter types can be registered
- Conflicting parameter names aren't detected
- Function config structures that executor expects may be missing
- Schema design issues (like non-Optional fields) aren't caught at registration time

These errors surface during recipe execution or template validation, forcing recipe authors to debug plugin issues. Plugin validation at registration shifts this burden left to plugin authors where it belongs.

**Required Checks:**
* [x] **Associated Ticket/Epic** link is included above.
* [x] **Feature Area/Component** is identified.
* [x] **Target Release/Milestone** is confirmed.

## Documentation & Prior Art Review

First, confirm the minimum required documentation has been reviewed for context.

* [x] `README.md` or project documentation reviewed.
* [x] Existing architecture documentation or ADRs reviewed.
* [x] Related feature implementations or similar code reviewed.
* [x] API documentation or interface specs reviewed (if applicable).

| Document Type | Link / Location | Key Findings / Action Required |
| :--- | :--- | :--- |
| **ADR-016** | [docs/adr/ADR-016-schema-validation-error-handling.md](docs/adr/ADR-016-schema-validation-error-handling.md) | **Finding:** Establishes fail-fast validation principle. Plugin registration validation is the natural extension - catch errors at earliest possible point. **Action:** Reference ADR-016, add section about plugin registration validation. |
| **Recipe Validation** | [core/recipe_validation.py](core/recipe_validation.py) | **Finding:** Already validates recipe template usage of functions. Plugin validation is complementary - validates function definitions. **Action:** Follow similar validation pattern (validator class, clear errors). |
| **Plugin Registration** | [core/registration/domains.py](core/registration/domains.py) | **Finding:** Current registration accepts any function definition. No schema validation present. **Action:** Add validation step before accepting registration. |
| **Function Models** | [core/models.py](core/models.py) FunctionDefinition | **Finding:** FunctionDefinition has schema field but no validation logic. **Action:** Add validation methods to model or separate validator. |
| **Executor Integration** | [core/executor.py](core/executor.py) | **Finding:** Executor expects certain function config structure. Should validate this at registration. **Action:** Define executor's schema requirements clearly. |
| **Schema Validation** | [core/schemas.py](core/schemas.py) | **Finding:** Already has schema validation for domain models. Can reuse patterns. **Action:** Extract common validation logic if applicable. |

## Design & Planning

### Initial Design Thoughts & Requirements

**Core Requirements:**
* Validate function schemas have all required fields before registration
* Check that required parameters are defined with proper types
* Detect conflicting parameter names
* Validate parameter default values match their declared types
* Ensure function config structure matches executor expectations
* Provide clear, actionable error messages for plugin authors
* Fast validation (< 10ms per function, registration is one-time cost)
* Fail registration immediately if schema invalid

**Design Approach:**

**1. Validation Layers (similar to recipe validation):**
   - **Layer 1: Schema Structure Validation**
     * Required fields present (name, description, parameters, etc.)
     * Field types correct (parameters is dict/list, not string)
     * No unexpected/typo fields
   
   - **Layer 2: Parameter Schema Validation**
     * Required parameters defined
     * Parameter types are valid (string, int, bool, dict, list, etc.)
     * Default values match parameter types
     * No duplicate parameter names
     * Parameter names follow conventions (snake_case, no reserved words)
   
   - **Layer 3: Executor Contract Validation**
     * Function config structure matches executor expectations
     * Storage functions have document_id parameter
     * LLM functions have prompt/model parameters
     * Required outputs defined for functions that chain

**2. Where Validation Runs:**
   - In `core/registration/domains.py` during `register_function()` call
   - Before function is added to registry
   - Raises `FunctionSchemaValidationError` if invalid

**3. Error Reporting:**
   - Group errors by validation layer
   - Include function name and plugin name in context
   - Suggest fixes (e.g., "Parameter 'document_id' required for storage.update function")
   - Reference schema documentation for plugin authors

**4. Integration Points:**
   - Registration flow: validate → register → available for recipes
   - Recipe validation uses registered functions (assumes schemas valid)
   - Documentation: Plugin authoring guide with schema requirements

**Constraints:**
* Must not break existing valid plugins (backward compatible)
* Should provide migration guide for plugins with invalid schemas
* Validation should be comprehensive but not overly strict (allow flexibility)
* Error messages must be clear enough for plugin authors to self-fix

**Dependencies:**
* FunctionDefinition model (already exists)
* Plugin registration system (already exists)
* Pydantic for schema validation (already available)

### Acceptance Criteria

- [ ] Function schemas are validated automatically during plugin registration
- [ ] Missing required parameters are caught and reported with function context
- [ ] Invalid parameter types (non-existent types) are caught and reported
- [ ] Duplicate parameter names are detected and reported
- [ ] Default values that don't match parameter types are caught
- [ ] Validation errors halt registration with clear error message
- [ ] Error messages include function name, plugin name, and specific problem
- [ ] Validation adds < 10ms overhead per function (one-time cost at registration)
- [ ] All existing valid plugins continue to register successfully
- [ ] Validation provides suggestions for common schema errors
- [ ] Plugin authoring documentation updated with schema requirements

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | This card | - [ ] Design Complete |
| **Test Plan Creation** | TDD - tests written first | - [ ] Test Plan Approved |
| **TDD Implementation** | core/registration/, new function_schema_validator.py | - [ ] Implementation Complete |
| **Integration Testing** | Test with valid/invalid plugin definitions | - [ ] Integration Tests Pass |
| **Documentation** | Update plugin authoring guide, ADR-016 | - [ ] Documentation Complete |
| **Code Review** | PR review process | - [ ] Code Review Approved |
| **Deployment Plan** | Immediate - part of core registration | - [ ] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | Create test fixtures for invalid function schemas | - [ ] Failing tests are committed and documented |
| **2. Implement Feature Code** | Add FunctionSchemaValidator and integrate into registration | - [ ] Feature implementation is complete |
| **3. Run Passing Tests** | All validation tests pass | - [ ] Originally failing tests now pass |
| **4. Refactor** | Extract validation logic, clean code structure | - [ ] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | Run all registration tests, ensure no regressions | - [ ] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | Validate < 10ms overhead per function | - [ ] Performance requirements are met |

### Implementation Notes

**Test Strategy:**
- Create fixture function schemas with various validation errors:
  - `function_missing_parameters.yaml` - no parameters field
  - `function_invalid_parameter_type.yaml` - parameter type doesn't exist
  - `function_duplicate_params.yaml` - duplicate parameter names
  - `function_type_mismatch_default.yaml` - default value doesn't match type
  - `function_missing_required.yaml` - storage function without document_id
- Test that valid function schemas pass without errors
- Test that error messages are clear and actionable
- Performance test with 100+ function registrations

**Key Implementation Decisions:**
- Use separate `FunctionSchemaValidator` class similar to `RecipeValidator`
- Validation runs in `register_function()` before adding to registry
- Pydantic for type validation where applicable
- Fail-fast approach: first error halts registration
- Provide migration guide for plugins that need schema fixes

**Implementation Phases:**

**Phase 1: Basic Schema Structure Validation**
- Validate required fields present (name, description, parameters)
- Check field types are correct
- Report structural errors with function context

**Phase 2: Parameter Schema Validation**
- Validate each parameter has required fields (name, type)
- Check parameter types are valid
- Detect duplicate parameter names
- Validate default values match types

**Phase 3: Executor Contract Validation**
- Storage functions must have document_id parameter
- LLM functions must have prompt/model parameters
- Condition syntax validation (if present)
- Required outputs for chainable functions

**Phase 4: Integration & Documentation**
- Integrate into registration flow
- Update plugin authoring guide
- Update ADR-016 with registration validation
- Migration guide for existing plugins

**Code Structure:**
```python
# In core/registration/function_schema_validator.py

class FunctionSchemaValidator:
    """Validates function schemas before registration."""
    
    def __init__(self, function_def: FunctionDefinition, plugin_name: str):
        self.function_def = function_def
        self.plugin_name = plugin_name
    
    def validate(self) -> List[ValidationError]:
        """Run all validation checks, return list of errors."""
        errors = []
        errors.extend(self._validate_schema_structure())
        errors.extend(self._validate_parameters())
        errors.extend(self._validate_executor_contract())
        return errors
    
    def _validate_schema_structure(self) -> List[ValidationError]:
        """Validate required fields and types."""
        pass
    
    def _validate_parameters(self) -> List[ValidationError]:
        """Validate parameter definitions."""
        pass
    
    def _validate_executor_contract(self) -> List[ValidationError]:
        """Validate function meets executor expectations."""
        pass

# In core/registration/domains.py:
def register_function(function_def: FunctionDefinition, plugin_name: str):
    # Validate schema before registration
    validator = FunctionSchemaValidator(function_def, plugin_name)
    errors = validator.validate()
    if errors:
        error_msg = format_validation_errors(errors)
        raise FunctionSchemaValidationError(error_msg)
    
    # Proceed with registration...
```

**Error Message Format:**
```
Function Schema Validation Failed: my_plugin.storage.custom_save

1. Missing Required Parameter:
   - Function 'custom_save' is a storage function but missing required parameter 'document_id'
   - Suggestion: Add parameter: {"name": "document_id", "type": "string", "required": true}

2. Invalid Parameter Type:
   - Parameter 'count' has invalid type 'integer' (should be 'int')
   - Suggestion: Change type to one of: string, int, float, bool, dict, list

3. Type Mismatch:
   - Parameter 'enabled' has type 'bool' but default value is "true" (string)
   - Suggestion: Change default to: true (boolean, not string)

See docs/guides/plugin-authoring.md for function schema requirements.
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | [Link to approved PR] |
| **QA Verification** | [Verified by testing with valid/invalid plugins] |
| **Integration Testing** | [All existing plugins register successfully] |
| **Documentation** | [Plugin authoring guide updated with schema requirements] |
| **ADR-016 Update** | [Added section on plugin registration validation] |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Migration Guide?** | [Create migration guide for plugins with invalid schemas] |
| **Plugin Audit?** | [Audit existing plugins for schema compliance before deploying] |
| **LSP Integration?** | [Future: IDE integration for real-time function schema validation] |
| **Schema Documentation?** | [Create comprehensive function schema reference doc] |

### Completion Checklist

* [ ] All acceptance criteria are met and verified.
* [ ] All tests are passing (unit, integration, e2e, performance).
* [ ] Code review is approved and PR is merged.
* [ ] Documentation is updated (plugin authoring guide, schema reference).
* [ ] ADR-016 is updated with plugin registration validation section.
* [ ] Feature is deployed (merged to main).
* [ ] Existing plugins tested and confirmed compatible.
* [ ] Migration guide created for plugin authors (if needed).
* [ ] Follow-up actions are documented and tickets created.

---

## Relationship to Validation Architecture

This feature completes the three-layer validation architecture:

**Layer 1: Plugin Registration (NEW - this card)**
- Validates function schemas are correct when plugins install
- Catches plugin authoring errors immediately
- Ensures executor can safely use registered functions

**Layer 2: Recipe Template Validation (Card oroau2 - COMPLETE)**
- Validates recipes use registered functions correctly
- Catches undefined link references and syntax errors
- Runs before recipe execution starts

**Layer 3: Domain Schema Validation (ADR-016 - COMPLETE)**
- Validates domain model schemas follow design principles
- Ensures Optional fields allow null values
- Validates model-level requirements

Together, these three layers provide comprehensive fail-fast validation from plugin authoring through recipe execution, following ADR-016 principles.
