"""
TDD Tests for llm.enrich link type

Tests the LLMEnrichLink handler which enriches documents with new information
using document-aware LLM extraction.

Test Categories:
1. Registration - Link type is registered and accessible
2. Document Context - Receives and uses full document context
3. Target Field Extraction - Populates specified target fields
4. Field Preservation - Preserves all existing document fields
5. Context-Aware Inference - LLM sees existing values
6. Auto Field Detection - Supports target_fields: "auto"
7. Multiple Target Fields - Handles multiple fields in one call
8. Output Structure - Returns complete enriched document
9. Template Rendering - Renders Jinja2 templates in config
10. Error Handling - Handles enrichment failures gracefully
11. Link Schema - Provides valid JSON schema
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from core.links import get_link_handler
from core.domains.llm.links import LLMEnrichLink


# ==============================================================================
# Test Category 1: Registration
# ==============================================================================

class TestLLMEnrichRegistration:
    """Tests for llm.enrich link type registration."""
    
    def test_llm_enrich_is_registered(self):
        """llm.enrich should be registered as a link type."""
        handler = get_link_handler("llm.enrich")
        assert handler is not None
    
    def test_llm_enrich_returns_correct_handler(self):
        """llm.enrich should return LLMEnrichLink handler."""
        handler = get_link_handler("llm.enrich")
        assert handler == LLMEnrichLink
    
    def test_llm_enrich_has_execute_method(self):
        """LLMEnrichLink should have an execute method."""
        assert hasattr(LLMEnrichLink, "execute")
        assert callable(getattr(LLMEnrichLink, "execute"))


# ==============================================================================
# Test Category 2: Document Context
# ==============================================================================

class TestLLMEnrichDocumentContext:
    """Tests for document context handling."""
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_receives_full_document(self, mock_llm):
        """Should receive full document context including schema and data."""
        mock_llm.return_value = {
            "english_word": "woman",
            "connotation": "of marriageable age",
            "origin_words": [{"word": "fael", "meaning": "grace"}]
        }
        
        document = {
            "schema": {
                "type": "object",
                "properties": {
                    "english_word": {"type": "string"},
                    "connotation": {"type": "string"},
                    "origin_words": {"type": "array"}
                }
            },
            "data": {
                "english_word": "woman",
                "connotation": "of marriageable age",
                "origin_words": None
            }
        }
        
        config = {
            "type": "llm.enrich",
            "document": document,
            "source": "The word derives from fael (grace).",
            "target_fields": ["origin_words"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        # Verify LLM was called
        mock_llm.assert_called_once()
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_resolves_document_from_context_template(self, mock_llm):
        """Should resolve document from context via template."""
        mock_llm.return_value = {"field": "value", "new_field": "enriched"}
        
        config = {
            "type": "llm.enrich",
            "document": "{{ Working_Doc.data }}",
            "source": "New information",
            "target_fields": ["new_field"]
        }
        context = {
            "Working_Doc": {
                "data": {
                    "schema": {"type": "object"},
                    "data": {"field": "value", "new_field": None}
                }
            }
        }
        
        result = LLMEnrichLink.execute(config, context)
        
        mock_llm.assert_called_once()


# ==============================================================================
# Test Category 3: Target Field Extraction
# ==============================================================================

class TestLLMEnrichTargetFields:
    """Tests for populating target fields."""
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_populates_single_target_field(self, mock_llm):
        """Should populate a single target field."""
        mock_llm.return_value = {
            "name": "Alice",
            "age": 30  # Target field populated
        }
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object", "properties": {"name": {}, "age": {}}},
                "data": {"name": "Alice", "age": None}
            },
            "source": "Alice is 30 years old.",
            "target_fields": ["age"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"]["age"] == 30
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_populates_multiple_target_fields(self, mock_llm):
        """Should populate multiple target fields in one call."""
        mock_llm.return_value = {
            "english_word": "woman",
            "connotation": "of marriageable age",
            "origin_words": [{"word": "fael", "meaning": "grace"}],
            "revised_connotation": "graceful young womanhood"
        }
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object"},
                "data": {
                    "english_word": "woman",
                    "connotation": "of marriageable age",
                    "origin_words": None,
                    "revised_connotation": None
                }
            },
            "source": "The word derives from fael (grace)...",
            "target_fields": ["origin_words", "revised_connotation"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"]["origin_words"] is not None
        assert result["data"]["revised_connotation"] is not None


# ==============================================================================
# Test Category 4: Field Preservation
# ==============================================================================

class TestLLMEnrichFieldPreservation:
    """Tests for preserving existing document fields."""
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_preserves_existing_string_fields(self, mock_llm):
        """Should preserve existing string fields."""
        mock_llm.return_value = {
            "existing_field": "original value",
            "new_field": "enriched value"
        }
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object"},
                "data": {
                    "existing_field": "original value",
                    "new_field": None
                }
            },
            "source": "Source text",
            "target_fields": ["new_field"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"]["existing_field"] == "original value"
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_preserves_existing_complex_fields(self, mock_llm):
        """Should preserve existing complex fields (arrays, objects)."""
        existing_array = [{"id": 1}, {"id": 2}]
        mock_llm.return_value = {
            "existing_array": existing_array,
            "new_field": "enriched"
        }
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object"},
                "data": {
                    "existing_array": existing_array,
                    "new_field": None
                }
            },
            "source": "Source",
            "target_fields": ["new_field"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"]["existing_array"] == existing_array


# ==============================================================================
# Test Category 5: Context-Aware Inference
# ==============================================================================

class TestLLMEnrichContextAwareness:
    """Tests for context-aware LLM inference."""
    
    def test_build_enrichment_prompt_includes_current_state(self):
        """Prompt should include current document state."""
        current_data = {
            "english_word": "woman",
            "connotation": "of marriageable age"
        }
        
        prompt = LLMEnrichLink._build_enrichment_prompt(
            current_data=current_data,
            source="New info",
            target_fields=["origin_words"],
            schema={},
            hint=""
        )
        
        assert "CURRENT DOCUMENT STATE" in prompt
        assert "woman" in prompt
    
    def test_build_enrichment_prompt_identifies_target_fields(self):
        """Prompt should clearly identify target fields."""
        prompt = LLMEnrichLink._build_enrichment_prompt(
            current_data={"field1": "value", "field2": None},
            source="Source",
            target_fields=["field2", "field3"],
            schema={},
            hint=""
        )
        
        assert "TARGET FIELDS" in prompt
        assert "field2" in prompt
        assert "field3" in prompt
    
    def test_build_enrichment_prompt_includes_source(self):
        """Prompt should include source text."""
        prompt = LLMEnrichLink._build_enrichment_prompt(
            current_data={},
            source="Important source information here.",
            target_fields=["field"],
            schema={},
            hint=""
        )
        
        assert "Important source information here." in prompt


# ==============================================================================
# Test Category 6: Auto Field Detection
# ==============================================================================

class TestLLMEnrichAutoFieldDetection:
    """Tests for automatic target field detection."""
    
    def test_find_empty_fields_detects_null_fields(self):
        """Should detect fields with null values."""
        data = {
            "populated": "value",
            "empty_null": None,
            "empty_none": None
        }
        schema = {
            "type": "object",
            "properties": {
                "populated": {"type": "string"},
                "empty_null": {"type": "string"},
                "empty_none": {"type": "string"}
            }
        }
        
        empty_fields = LLMEnrichLink._find_empty_fields(data, schema)
        
        assert "populated" not in empty_fields
        assert "empty_null" in empty_fields
        assert "empty_none" in empty_fields
    
    def test_find_empty_fields_detects_empty_arrays(self):
        """Should detect empty array fields."""
        data = {
            "populated_array": [1, 2, 3],
            "empty_array": [],
            "null_array": None
        }
        schema = {"type": "object", "properties": {}}
        
        empty_fields = LLMEnrichLink._find_empty_fields(data, schema)
        
        assert "populated_array" not in empty_fields
        assert "empty_array" in empty_fields
        assert "null_array" in empty_fields
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_auto_target_fields_uses_empty_detection(self, mock_llm):
        """target_fields: 'auto' should use empty field detection."""
        mock_llm.return_value = {
            "populated": "existing",
            "empty_field": "enriched"
        }
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object", "properties": {"populated": {}, "empty_field": {}}},
                "data": {
                    "populated": "existing",
                    "empty_field": None
                }
            },
            "source": "Source text",
            "target_fields": "auto"
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        # Should have enriched the empty field
        assert "data" in result


# ==============================================================================
# Test Category 7: Output Structure
# ==============================================================================

class TestLLMEnrichOutputStructure:
    """Tests for output format."""
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_returns_raw_and_data(self, mock_llm):
        """Should return both raw prompt and enriched data."""
        mock_llm.return_value = {"field": "value"}
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object"},
                "data": {"field": None}
            },
            "source": "Source",
            "target_fields": ["field"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert "raw" in result
        assert "data" in result
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_data_is_complete_document(self, mock_llm):
        """Data should be the complete enriched document."""
        mock_llm.return_value = {
            "existing": "value",
            "enriched": "new_value"
        }
        
        config = {
            "type": "llm.enrich",
            "document": {
                "schema": {"type": "object"},
                "data": {
                    "existing": "value",
                    "enriched": None
                }
            },
            "source": "Source",
            "target_fields": ["enriched"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"]["existing"] == "value"
        assert result["data"]["enriched"] == "new_value"


# ==============================================================================
# Test Category 8: Template Rendering
# ==============================================================================

class TestLLMEnrichTemplateRendering:
    """Tests for Jinja2 template rendering."""
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_renders_source_from_context(self, mock_llm):
        """Should render source text from context template."""
        mock_llm.return_value = {"field": "value"}
        
        config = {
            "type": "llm.enrich",
            "document": {"schema": {}, "data": {"field": None}},
            "source": "{{ Generate_Origins.data.raw }}",
            "target_fields": ["field"]
        }
        context = {
            "Generate_Origins": {
                "data": {"raw": "The etymology is fael-neth-wen."}
            }
        }
        
        result = LLMEnrichLink.execute(config, context)
        
        assert "fael-neth-wen" in result.get("raw", "")
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_renders_hint_from_context(self, mock_llm):
        """Should render hint from context template."""
        mock_llm.return_value = {}
        
        config = {
            "type": "llm.enrich",
            "document": {"schema": {}, "data": {}},
            "source": "Source",
            "target_fields": [],
            "hint": "{{ guidance }}"
        }
        context = {"guidance": "Focus on Sylvan roots"}
        
        result = LLMEnrichLink.execute(config, context)
        
        assert "Sylvan roots" in result.get("raw", "")


# ==============================================================================
# Test Category 9: Error Handling
# ==============================================================================

class TestLLMEnrichErrorHandling:
    """Tests for error handling."""
    
    def test_handles_missing_document(self):
        """Should return error when document not provided."""
        config = {
            "type": "llm.enrich",
            # Missing document
            "source": "Source",
            "target_fields": ["field"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]
    
    def test_handles_missing_source(self):
        """Should return error when source not provided."""
        config = {
            "type": "llm.enrich",
            "document": {"schema": {}, "data": {}},
            # Missing source
            "target_fields": ["field"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_handles_llm_failure(self, mock_llm):
        """Should handle LLM call failures gracefully."""
        mock_llm.side_effect = Exception("API Error")
        
        config = {
            "type": "llm.enrich",
            "document": {"schema": {}, "data": {"field": None}},
            "source": "Source",
            "target_fields": ["field"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        assert result["data"].get("success") is False or "error" in result["data"]


# ==============================================================================
# Test Category 10: Link Schema
# ==============================================================================

class TestLLMEnrichLinkSchema:
    """Tests for link type JSON schema."""
    
    def test_has_get_schema_method(self):
        """Should have get_schema class method."""
        assert hasattr(LLMEnrichLink, "get_schema")
        assert callable(getattr(LLMEnrichLink, "get_schema"))
    
    def test_schema_includes_required_fields(self):
        """Schema should define type, document, source as required."""
        schema = LLMEnrichLink.get_schema()
        
        assert "required" in schema
        assert "type" in schema["required"]
        assert "document" in schema["required"]
        assert "source" in schema["required"]
    
    def test_schema_includes_all_properties(self):
        """Schema should define all link properties."""
        schema = LLMEnrichLink.get_schema()
        
        props = schema.get("properties", {})
        assert "type" in props
        assert "document" in props
        assert "source" in props
        assert "target_fields" in props
        assert "hint" in props


# ==============================================================================
# Test Category 11: Integration with Document Workflow
# ==============================================================================

class TestLLMEnrichDocumentWorkflow:
    """Tests for integration with storage workflow."""
    
    @patch.object(LLMEnrichLink, '_call_llm_json_mode')
    def test_works_with_storage_init_output(self, mock_llm):
        """Should work with storage.init document format."""
        mock_llm.return_value = {
            "english_word": "woman",
            "connotation": "of marriageable age",
            "origin_words": [
                {"word": "fael", "meaning": "grace"},
                {"word": "neth", "meaning": "youth"}
            ],
            "eldorian_word": None
        }
        
        # Simulates storage.init output
        working_doc = {
            "id": "doc-abc123",
            "collection": "words",
            "schema": {
                "type": "object",
                "properties": {
                    "english_word": {"type": "string"},
                    "connotation": {"type": "string"},
                    "origin_words": {"type": "array"},
                    "eldorian_word": {"type": "string"}
                }
            },
            "data": {
                "english_word": "woman",
                "connotation": "of marriageable age",
                "origin_words": None,
                "eldorian_word": None
            }
        }
        
        config = {
            "type": "llm.enrich",
            "document": working_doc,
            "source": "The word derives from fael (grace) and neth (youth).",
            "target_fields": ["origin_words"]
        }
        
        result = LLMEnrichLink.execute(config, {})
        
        # Should have enriched origin_words
        assert len(result["data"]["origin_words"]) == 2
        # Should preserve existing fields
        assert result["data"]["english_word"] == "woman"
