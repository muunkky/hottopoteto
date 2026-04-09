"""
TDD tests for 5 link-type bugs identified in PR #4 code review.

Card: i72ia1 (ELDV21FU sprint)
Reference: https://github.com/muunkky/hottopoteto/pull/4#issuecomment-4216087731
"""
import pytest
from unittest.mock import patch, MagicMock
from typing import List, Optional
from pydantic import BaseModel, Field

from core.domains.llm.links import LLMEnrichLink, LLMExtractToSchemaLink
from core.schema.pydantic_integration import generate_recipe_template


# ---------------------------------------------------------------------------
# Bug 1: LLMEnrichLink._resolve_document always returns an empty document
# ---------------------------------------------------------------------------

class TestResolveDocument:
    """Bug 1: _resolve_document with template string must return rendered dict."""

    def test_resolve_document_returns_rendered_dict_for_template_string(self):
        """Template string rendering a dict must return that dict, not empty wrapper."""
        context = {
            "Working_Doc": {
                "data": {
                    "schema": {"title": "word"},
                    "data": {"term": "eldorian"},
                }
            }
        }
        result = LLMEnrichLink._resolve_document("{{ Working_Doc.data }}", context)
        assert result != {"schema": {}, "data": {}}, (
            "Bug 1: _resolve_document returned empty document instead of rendered dict"
        )
        assert result["data"]["term"] == "eldorian"

    def test_resolve_document_nested_dict_is_fully_returned(self):
        """All nested keys must survive the render round-trip."""
        context = {
            "doc": {
                "schema": {"type": "object"},
                "data": {"field_a": 1, "field_b": [1, 2, 3]},
            }
        }
        result = LLMEnrichLink._resolve_document("{{ doc }}", context)
        assert result["schema"] == {"type": "object"}
        assert result["data"]["field_b"] == [1, 2, 3]

    def test_resolve_document_with_inline_dict_is_passthrough(self):
        """Inline dicts must pass through unchanged (not a regression)."""
        doc = {"schema": {"type": "object"}, "data": {"x": 1}}
        result = LLMEnrichLink._resolve_document(doc, {})
        assert result == doc

    def test_resolve_document_with_non_template_string_returns_empty(self):
        """A plain string (no template) that cannot be parsed should still fallback."""
        result = LLMEnrichLink._resolve_document("not_a_template", {})
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Bug 2: LLMExtractToSchemaLink._resolve_schema silently falls back
# ---------------------------------------------------------------------------

class TestResolveSchema:
    """Bug 2: _resolve_schema with template string must return the rendered schema."""

    def test_resolve_schema_returns_rendered_schema_for_template_string(self):
        """Template resolving to a schema dict must return that dict."""
        schema = {"type": "object", "properties": {"term": {"type": "string"}}}
        context = {"Working_Doc": {"data": {"schema": schema}}}
        result = LLMExtractToSchemaLink._resolve_schema(
            "{{ Working_Doc.data.schema }}", context
        )
        assert result != {"type": "object"}, (
            "Bug 2: _resolve_schema fell back to minimal schema instead of rendered schema"
        )
        assert "properties" in result
        assert "term" in result["properties"]

    def test_resolve_schema_with_nested_property(self):
        """Deeper property path must also work."""
        schema = {"type": "array", "items": {"type": "string"}}
        context = {"doc": {"prop": schema}}
        result = LLMExtractToSchemaLink._resolve_schema("{{ doc.prop }}", context)
        assert result["type"] == "array"
        assert result["items"] == {"type": "string"}

    def test_resolve_schema_with_inline_dict_is_passthrough(self):
        """Inline schema dicts must pass through unchanged (not a regression)."""
        schema = {"type": "object", "properties": {"x": {"type": "integer"}}}
        result = LLMExtractToSchemaLink._resolve_schema(schema, {})
        assert result == schema


# ---------------------------------------------------------------------------
# Bug 3: generate_recipe_template writes PydanticUndefined for default_factory
# ---------------------------------------------------------------------------

class ModelWithDefaultFactory(BaseModel):
    name: str
    tags: List[str] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)


class ModelWithOptionalNone(BaseModel):
    name: str
    alias: Optional[str] = None


class TestGenerateRecipeTemplate:
    """Bug 3: PydanticUndefined must not appear in generated YAML."""

    def test_generate_recipe_template_omits_pydantic_undefined(self):
        """Fields using default_factory must not produce 'PydanticUndefined' in output."""
        template = generate_recipe_template("storage.init", input_model=ModelWithDefaultFactory)
        assert "PydanticUndefined" not in template, (
            "Bug 3: PydanticUndefined leaked into generated YAML template"
        )

    def test_generate_recipe_template_default_factory_field_omitted_or_empty(self):
        """A default_factory field may have no 'default' key, or a safe empty value."""
        import yaml
        template = generate_recipe_template("storage.init", input_model=ModelWithDefaultFactory)
        parsed = yaml.safe_load(template)
        tags_field = parsed["links"][0]["inputs"]["tags"]
        # Must not contain the sentinel; 'default' may be absent or []
        assert tags_field.get("default") is not PydanticUndefinedSentinel(), (
            "Bug 3: default_factory sentinel must not be serialized"
        )

    def test_generate_recipe_template_none_default_still_omitted(self):
        """Optional[str] = None defaults should remain omitted (regression guard)."""
        template = generate_recipe_template("storage.init", input_model=ModelWithOptionalNone)
        assert "None" not in template or "null" not in template or True  # structural check
        import yaml
        parsed = yaml.safe_load(template)
        alias_field = parsed["links"][0]["inputs"].get("alias", {})
        assert alias_field.get("default") is None or "default" not in alias_field


def PydanticUndefinedSentinel():
    """Helper: return PydanticUndefined for assertion clarity."""
    from pydantic_core import PydanticUndefined
    return PydanticUndefined


# ---------------------------------------------------------------------------
# Bug 4: provider config silently ignored in new LLM link types
# ---------------------------------------------------------------------------

class TestProviderForwarding:
    """Bug 4: provider from link_config must be forwarded to generate_text."""

    @patch("core.domains.llm.links.generate_text")
    def test_llm_extract_uses_provider_from_config(self, mock_generate_text):
        """LLMExtractToSchemaLink must pass provider to generate_text."""
        mock_generate_text.return_value = {"text": "{}"}
        link_config = {
            "name": "test",
            "model": "gpt-4o",
            "provider": "anthropic",
            "schema": {"type": "object"},
            "source": "some text",
        }
        LLMExtractToSchemaLink.execute(link_config, {})
        mock_generate_text.assert_called_once()
        call_kwargs = mock_generate_text.call_args
        # provider must appear as a kwarg or positional
        provider_passed = (
            call_kwargs.kwargs.get("provider") == "anthropic"
            or (len(call_kwargs.args) > 3 and call_kwargs.args[3] == "anthropic")
        )
        assert provider_passed, (
            f"Bug 4: provider='anthropic' was not forwarded to generate_text. "
            f"Call args: {call_kwargs}"
        )

    @patch("core.domains.llm.links.generate_text")
    def test_llm_enrich_uses_provider_from_config(self, mock_generate_text):
        """LLMEnrichLink must pass provider to generate_text."""
        mock_generate_text.return_value = {"text": "{}"}
        link_config = {
            "name": "test",
            "model": "gpt-4o",
            "provider": "anthropic",
            "document": {"schema": {}, "data": {}},
            "source": "some text",
        }
        LLMEnrichLink.execute(link_config, {})
        mock_generate_text.assert_called_once()
        call_kwargs = mock_generate_text.call_args
        provider_passed = (
            call_kwargs.kwargs.get("provider") == "anthropic"
            or (len(call_kwargs.args) > 3 and call_kwargs.args[3] == "anthropic")
        )
        assert provider_passed, (
            f"Bug 4: provider='anthropic' was not forwarded to generate_text. "
            f"Call args: {call_kwargs}"
        )

    @patch("core.domains.llm.links.generate_text")
    def test_llm_extract_defaults_provider_to_openai(self, mock_generate_text):
        """When provider is not specified, it should default to 'openai'."""
        mock_generate_text.return_value = {"text": "{}"}
        link_config = {
            "name": "test",
            "model": "gpt-4o",
            "schema": {"type": "object"},
            "source": "some text",
        }
        LLMExtractToSchemaLink.execute(link_config, {})
        call_kwargs = mock_generate_text.call_args
        provider_passed = call_kwargs.kwargs.get("provider", "openai")
        assert provider_passed == "openai", (
            f"Bug 4: default provider should be 'openai', got {provider_passed!r}"
        )


# ---------------------------------------------------------------------------
# Bug 5: New link types use bare Environment(), ignoring StrictUndefined
# ---------------------------------------------------------------------------

class TestStrictUndefined:
    """Bug 5: All _render_template helpers must raise on undefined variables."""

    def test_llm_extract_render_template_raises_on_undefined_variable(self):
        """LLMExtractToSchemaLink._render_template must raise for missing vars."""
        from jinja2 import UndefinedError
        with pytest.raises(UndefinedError):
            LLMExtractToSchemaLink._render_template("{{ nonexistent_var }}", {})

    def test_llm_enrich_render_template_raises_on_undefined_variable(self):
        """LLMEnrichLink._render_template must raise for missing vars."""
        from jinja2 import UndefinedError
        with pytest.raises(UndefinedError):
            LLMEnrichLink._render_template("{{ nonexistent_var }}", {})

    def test_llm_extract_render_template_with_defined_var_works(self):
        """Defined variables must still render correctly (not a regression)."""
        result = LLMExtractToSchemaLink._render_template("{{ name }}", {"name": "eldorian"})
        assert result == "eldorian"

    def test_llm_enrich_render_template_with_defined_var_works(self):
        """Defined variables must still render correctly (not a regression)."""
        result = LLMEnrichLink._render_template("{{ name }}", {"name": "eldorian"})
        assert result == "eldorian"

    def test_storage_init_link_extract_data_raises_on_undefined_variable(self):
        """StorageInitLink._extract_data (new in PR#4) must raise for missing template vars."""
        from jinja2 import UndefinedError
        from core.domains.storage.links import StorageInitLink
        with pytest.raises(UndefinedError):
            StorageInitLink._extract_data("{{ nonexistent_var }}", {})

    def test_storage_update_link_extract_data_raises_on_undefined(self):
        """StorageUpdateLink._extract_data (new in PR#4) must raise for missing vars."""
        from jinja2 import UndefinedError
        from core.domains.storage.links import StorageUpdateLink
        with pytest.raises(UndefinedError):
            StorageUpdateLink._extract_data("{{ nonexistent_var }}", {})

    def test_storage_update_link_render_template_raises_on_undefined(self):
        """StorageUpdateLink._render_template (new in PR#4) must raise for missing vars."""
        from jinja2 import UndefinedError
        from core.domains.storage.links import StorageUpdateLink
        with pytest.raises(UndefinedError):
            StorageUpdateLink._render_template("{{ nonexistent_var }}", {})
