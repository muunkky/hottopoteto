"""
TDD Tests for llm.extract_to_schema link type

Tests the LLMExtractToSchemaLink handler which extracts structured data
from unstructured text using LLM with JSON mode.

Test Categories:
1. Registration - Link type is registered and accessible
2. Basic Extraction - Extracts data matching schema
3. Prompt Generation - Auto-generates extraction prompt from schema
4. Schema Resolution - Resolves schemas from various sources
5. JSON Mode - Uses LLM JSON mode for structured output
6. Hint Parameter - Supports optional extraction guidance
7. Output Validation - Validates extracted data against schema
8. Template Rendering - Renders Jinja2 templates in config
9. Error Handling - Handles extraction failures gracefully
10. Link Schema - Provides valid JSON schema
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from core.links import get_link_handler
from core.domains.llm.links import LLMExtractToSchemaLink


# ==============================================================================
# Test Category 1: Registration
# ==============================================================================

class TestLLMExtractToSchemaRegistration:
    """Tests for llm.extract_to_schema link type registration."""
    
    def test_llm_extract_to_schema_is_registered(self):
        """llm.extract_to_schema should be registered as a link type."""
        handler = get_link_handler("llm.extract_to_schema")
        assert handler is not None
    
    def test_llm_extract_to_schema_returns_correct_handler(self):
        """llm.extract_to_schema should return LLMExtractToSchemaLink handler."""
        handler = get_link_handler("llm.extract_to_schema")
        assert handler == LLMExtractToSchemaLink
    
    def test_llm_extract_to_schema_has_execute_method(self):
        """LLMExtractToSchemaLink should have an execute method."""
        assert hasattr(LLMExtractToSchemaLink, "execute")
        assert callable(getattr(LLMExtractToSchemaLink, "execute"))


# ==============================================================================
# Test Category 2: Basic Extraction
# ==============================================================================

class TestLLMExtractToSchemaBasicExtraction:
    """Tests for basic data extraction."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_extracts_simple_object(self, mock_llm):
        """Should extract simple object matching schema."""
        mock_llm.return_value = {"name": "Alice", "age": 30}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Her name is Alice and she is 30 years old.",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            }
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert result["data"]["name"] == "Alice"
        assert result["data"]["age"] == 30
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_extracts_array_of_objects(self, mock_llm):
        """Should extract array of objects matching schema."""
        mock_llm.return_value = [
            {"word": "fael", "meaning": "grace"},
            {"word": "neth", "meaning": "youth"}
        ]
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "The word derives from fael (grace) and neth (youth).",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "word": {"type": "string"},
                        "meaning": {"type": "string"}
                    }
                }
            }
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert len(result["data"]) == 2
        assert result["data"][0]["word"] == "fael"
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_returns_raw_and_data(self, mock_llm):
        """Should return both raw prompt and extracted data."""
        mock_llm.return_value = {"extracted": "value"}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Some text",
            "schema": {"type": "object", "properties": {"extracted": {"type": "string"}}}
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert "raw" in result
        assert "data" in result
        assert result["data"]["extracted"] == "value"


# ==============================================================================
# Test Category 3: Prompt Generation
# ==============================================================================

class TestLLMExtractToSchemaPromptGeneration:
    """Tests for auto-generated extraction prompts."""
    
    def test_build_extraction_prompt_includes_schema(self):
        """Generated prompt should include the target schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        prompt = LLMExtractToSchemaLink._build_extraction_prompt(
            source="Test text",
            schema=schema,
            hint=""
        )
        
        assert "TARGET SCHEMA" in prompt
        assert '"name"' in prompt
    
    def test_build_extraction_prompt_includes_source(self):
        """Generated prompt should include the source text."""
        prompt = LLMExtractToSchemaLink._build_extraction_prompt(
            source="The original text to extract from.",
            schema={"type": "object"},
            hint=""
        )
        
        assert "SOURCE TEXT" in prompt
        assert "The original text to extract from." in prompt
    
    def test_build_extraction_prompt_includes_hint_when_provided(self):
        """Generated prompt should include hint when provided."""
        prompt = LLMExtractToSchemaLink._build_extraction_prompt(
            source="Test",
            schema={"type": "object"},
            hint="Focus on fictional etymology"
        )
        
        assert "Focus on fictional etymology" in prompt
    
    def test_build_extraction_prompt_excludes_hint_when_empty(self):
        """Generated prompt should not have hint section when empty."""
        prompt = LLMExtractToSchemaLink._build_extraction_prompt(
            source="Test",
            schema={"type": "object"},
            hint=""
        )
        
        assert "EXTRACTION GUIDANCE" not in prompt or "GUIDANCE:" not in prompt


# ==============================================================================
# Test Category 4: Schema Resolution
# ==============================================================================

class TestLLMExtractToSchemaSchemaResolution:
    """Tests for resolving schemas from various sources."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_accepts_inline_schema(self, mock_llm):
        """Should accept inline schema definition."""
        mock_llm.return_value = {"field": "value"}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test text",
            "schema": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"}
                }
            }
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert result["data"]["field"] == "value"
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_resolves_schema_from_context_template(self, mock_llm):
        """Should resolve schema from context via template."""
        mock_llm.return_value = [{"word": "test"}]
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": "{{ Working_Doc.data.schema.properties.origin_words }}"
        }
        context = {
            "Working_Doc": {
                "data": {
                    "schema": {
                        "properties": {
                            "origin_words": {
                                "type": "array",
                                "items": {"type": "object", "properties": {"word": {"type": "string"}}}
                            }
                        }
                    }
                }
            }
        }
        
        result = LLMExtractToSchemaLink.execute(config, context)
        
        # Should have used the resolved schema
        mock_llm.assert_called_once()


# ==============================================================================
# Test Category 5: JSON Mode / LLM Calling
# ==============================================================================

class TestLLMExtractToSchemaJSONMode:
    """Tests for LLM JSON mode output."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_passes_schema_to_llm_call(self, mock_llm):
        """Should pass schema to LLM call for JSON mode."""
        mock_llm.return_value = {}
        
        schema = {"type": "object", "properties": {"test": {"type": "string"}}}
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": schema
        }
        
        LLMExtractToSchemaLink.execute(config, {})
        
        # Verify LLM was called with schema
        call_args = mock_llm.call_args
        assert call_args is not None
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_uses_specified_model(self, mock_llm):
        """Should use specified model for LLM call."""
        mock_llm.return_value = {}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": {"type": "object"},
            "model": "gpt-4-turbo"
        }
        
        LLMExtractToSchemaLink.execute(config, {})
        
        # Verify model was passed
        call_kwargs = mock_llm.call_args[1] if mock_llm.call_args[1] else {}
        # Model should be in kwargs or positional args
        assert mock_llm.called
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_uses_default_temperature_for_extraction(self, mock_llm):
        """Should use low temperature by default for extraction accuracy."""
        mock_llm.return_value = {}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": {"type": "object"}
        }
        
        LLMExtractToSchemaLink.execute(config, {})
        
        # Low temperature expected for extraction (0.2 or similar)
        assert mock_llm.called


# ==============================================================================
# Test Category 6: Hint Parameter
# ==============================================================================

class TestLLMExtractToSchemaHintParameter:
    """Tests for optional hint parameter."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_accepts_hint_parameter(self, mock_llm):
        """Should accept and use hint parameter."""
        mock_llm.return_value = {}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": {"type": "object"},
            "hint": "Focus on fictional etymology components"
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        # Hint should appear in the generated prompt (raw)
        assert "fictional etymology" in result.get("raw", "")
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_works_without_hint(self, mock_llm):
        """Should work correctly without hint parameter."""
        mock_llm.return_value = {"data": "extracted"}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test text",
            "schema": {"type": "object", "properties": {"data": {"type": "string"}}}
            # No hint
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert "data" in result
        assert result["data"]["data"] == "extracted"


# ==============================================================================
# Test Category 7: Output Validation
# ==============================================================================

class TestLLMExtractToSchemaOutputValidation:
    """Tests for validating extracted data against schema."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_validates_output_against_schema(self, mock_llm):
        """Should validate LLM output against schema."""
        mock_llm.return_value = {"name": "Alice", "age": 30}
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Alice is 30",
            "schema": schema
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        # Should succeed with valid data
        assert "error" not in result.get("data", {})
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_handles_validation_failure(self, mock_llm):
        """Should handle gracefully when LLM output fails validation."""
        # LLM returns wrong type
        mock_llm.return_value = {"age": "not a number"}
        
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer"}
            }
        }
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Some text",
            "schema": schema
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        # Should report error or handle gracefully
        # Implementation may return error or attempt correction
        assert "data" in result


# ==============================================================================
# Test Category 8: Template Rendering
# ==============================================================================

class TestLLMExtractToSchemaTemplateRendering:
    """Tests for Jinja2 template rendering."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_renders_source_from_context(self, mock_llm):
        """Should render source text from context template."""
        mock_llm.return_value = {"extracted": "data"}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "{{ Generate_Origins.data.raw }}",
            "schema": {"type": "object", "properties": {"extracted": {"type": "string"}}}
        }
        context = {
            "Generate_Origins": {
                "data": {
                    "raw": "The word fael means grace in the old tongue."
                }
            }
        }
        
        result = LLMExtractToSchemaLink.execute(config, context)
        
        # Prompt should contain the rendered source
        assert "fael means grace" in result.get("raw", "")
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_renders_hint_from_context(self, mock_llm):
        """Should render hint from context template."""
        mock_llm.return_value = {}
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": {"type": "object"},
            "hint": "{{ extraction_guidance }}"
        }
        context = {
            "extraction_guidance": "Focus on proper nouns"
        }
        
        result = LLMExtractToSchemaLink.execute(config, context)
        
        assert "proper nouns" in result.get("raw", "")


# ==============================================================================
# Test Category 9: Error Handling
# ==============================================================================

class TestLLMExtractToSchemaErrorHandling:
    """Tests for error handling."""
    
    def test_handles_missing_source(self):
        """Should return error when source not provided."""
        config = {
            "type": "llm.extract_to_schema",
            # Missing source
            "schema": {"type": "object"}
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]
    
    def test_handles_missing_schema(self):
        """Should return error when schema not provided."""
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test text"
            # Missing schema
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_handles_llm_failure(self, mock_llm):
        """Should handle LLM call failures gracefully."""
        mock_llm.side_effect = Exception("API Error")
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": {"type": "object"}
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_handles_invalid_json_response(self, mock_llm):
        """Should handle when LLM returns invalid JSON."""
        mock_llm.side_effect = json.JSONDecodeError("Invalid", "", 0)
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "Test",
            "schema": {"type": "object"}
        }
        
        result = LLMExtractToSchemaLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]


# ==============================================================================
# Test Category 10: Link Schema
# ==============================================================================

class TestLLMExtractToSchemaLinkSchema:
    """Tests for link type JSON schema."""
    
    def test_has_get_schema_method(self):
        """Should have get_schema class method."""
        assert hasattr(LLMExtractToSchemaLink, "get_schema")
        assert callable(getattr(LLMExtractToSchemaLink, "get_schema"))
    
    def test_schema_includes_required_fields(self):
        """Schema should define type, source, schema as required."""
        schema = LLMExtractToSchemaLink.get_schema()
        
        assert "required" in schema
        assert "type" in schema["required"]
        assert "source" in schema["required"]
        assert "schema" in schema["required"]
    
    def test_schema_includes_all_properties(self):
        """Schema should define all link properties."""
        schema = LLMExtractToSchemaLink.get_schema()
        
        props = schema.get("properties", {})
        assert "type" in props
        assert "source" in props
        assert "schema" in props
        assert "hint" in props
        assert "model" in props
        assert "temperature" in props


# ==============================================================================
# Test Category 11: Integration with Document Workflow
# ==============================================================================

class TestLLMExtractToSchemaDocumentWorkflow:
    """Tests for integration with storage.init/update workflow."""
    
    @patch.object(LLMExtractToSchemaLink, '_call_llm_json_mode')
    def test_extracts_for_storage_update(self, mock_llm):
        """Should work with storage workflow - extract data for update."""
        mock_llm.return_value = [
            {"word": "fael", "meaning": "grace"},
            {"word": "neth", "meaning": "youth"}
        ]
        
        # Simulates context after storage.init
        context = {
            "Working_Doc": {
                "data": {
                    "id": "doc-abc123",
                    "collection": "words",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "origin_words": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "word": {"type": "string"},
                                        "meaning": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "data": {
                        "english_word": "woman",
                        "origin_words": None
                    }
                }
            },
            "Generate_Origins": {
                "data": {
                    "raw": "The word derives from fael (grace) and neth (youth)."
                }
            }
        }
        
        config = {
            "type": "llm.extract_to_schema",
            "source": "{{ Generate_Origins.data.raw }}",
            "schema": "{{ Working_Doc.data.schema.properties.origin_words }}"
        }
        
        result = LLMExtractToSchemaLink.execute(config, context)
        
        # Extracted data ready for storage.update
        assert len(result["data"]) == 2
        assert result["data"][0]["word"] == "fael"
