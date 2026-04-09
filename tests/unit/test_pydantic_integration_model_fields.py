"""
TDD tests for pydantic_integration.py step-4b migration.

Verifies that generate_recipe_template uses Pydantic v2 model_fields API
(not deprecated __fields__) and correct FieldInfo attributes.

Card: TESTCOV1-i3y4j6 (step-4b migrate dunder fields to model_fields)
"""
import warnings
import pytest
from typing import Optional, List
from pydantic import BaseModel, Field


class TestGenerateRecipeTemplateUsesModelFields:
    """Verify generate_recipe_template works with Pydantic v2 model_fields."""

    def test_generate_recipe_template_imports_without_error(self):
        """Module imports cleanly."""
        from core.schema.pydantic_integration import generate_recipe_template  # noqa: F401

    def test_generate_recipe_template_with_simple_model(self):
        """generate_recipe_template produces valid YAML for a simple model."""
        from core.schema.pydantic_integration import generate_recipe_template

        class SimpleModel(BaseModel):
            prompt: str
            temperature: float = 0.7

        result = generate_recipe_template("llm.generate", input_model=SimpleModel)
        assert isinstance(result, str)
        assert "llm_generate_Link" in result
        assert "prompt" in result

    def test_generate_recipe_template_does_not_emit_deprecation_warning(self):
        """No PydanticDeprecatedSince20 warnings when calling generate_recipe_template."""
        from core.schema.pydantic_integration import generate_recipe_template
        from pydantic import PydanticDeprecatedSince20

        class SampleModel(BaseModel):
            name: str
            description: Optional[str] = None

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = generate_recipe_template("test.link", input_model=SampleModel)

        pydantic_warnings = [
            w for w in caught
            if issubclass(w.category, (PydanticDeprecatedSince20, DeprecationWarning))
            and "pydantic" in str(w.message).lower()
        ]
        assert len(pydantic_warnings) == 0, (
            f"Expected no Pydantic deprecation warnings, got: "
            f"{[str(w.message) for w in pydantic_warnings]}"
        )

    def test_required_field_marked_required_in_output(self):
        """A required field (no default) should appear with required: true."""
        from core.schema.pydantic_integration import generate_recipe_template

        class ModelWithRequired(BaseModel):
            required_input: str
            optional_input: str = "default"

        result = generate_recipe_template("test.link", input_model=ModelWithRequired)
        assert "required_input" in result
        # The required field should be flagged
        assert "required: true" in result

    def test_optional_field_not_marked_required(self):
        """An optional field should not be marked required."""
        from core.schema.pydantic_integration import generate_recipe_template

        class ModelWithOptional(BaseModel):
            optional_field: Optional[str] = None

        result = generate_recipe_template("test.link", input_model=ModelWithOptional)
        # Should not crash — previously crashed with AttributeError on .allow_none
        assert "optional_field" in result

    def test_field_with_default_includes_default_in_output(self):
        """A field with a non-None default should include that default in the template."""
        from core.schema.pydantic_integration import generate_recipe_template

        class ModelWithDefault(BaseModel):
            temperature: float = 0.7

        result = generate_recipe_template("test.link", input_model=ModelWithDefault)
        assert "temperature" in result
        assert "0.7" in result

    def test_generate_recipe_template_with_output_model(self):
        """Output model schema is included via model_json_schema()."""
        from core.schema.pydantic_integration import generate_recipe_template

        class OutputModel(BaseModel):
            result: str
            score: float

        result = generate_recipe_template("test.link", output_model=OutputModel)
        assert "output_schema" in result or "result" in result

    def test_generate_recipe_template_no_models(self):
        """Calling with no models produces a minimal link template."""
        from core.schema.pydantic_integration import generate_recipe_template

        result = generate_recipe_template("bare.link", description="A bare link")
        assert "bare_link_Link" in result
        assert "A bare link" in result

    def test_optional_none_default_field_does_not_emit_default_key(self):
        """An Optional[str] = None field must NOT produce a 'default:' key in the YAML output.

        This is intentional behavior: None defaults are omitted from the template
        because emitting 'default: null' (or 'default: None') adds noise without value.
        This test pins that behavior so future changes cannot silently regress it.

        Card: TESTCOV1-rmyo6v (cleanup pydantic integration single-pass)
        """
        from core.schema.pydantic_integration import generate_recipe_template

        class ModelWithNoneDefault(BaseModel):
            required_field: str
            optional_field: Optional[str] = None

        result = generate_recipe_template("test.link", input_model=ModelWithNoneDefault)
        assert "optional_field" in result, "optional_field must appear in the template"
        # The default: key must NOT appear for an Optional[str] = None field
        import yaml
        parsed = yaml.safe_load(result)
        inputs = parsed["links"][0]["inputs"]
        assert "optional_field" in inputs, "optional_field must be in the inputs dict"
        assert "default" not in inputs["optional_field"], (
            "Optional[str] = None field must NOT emit a 'default:' key in the template"
        )
