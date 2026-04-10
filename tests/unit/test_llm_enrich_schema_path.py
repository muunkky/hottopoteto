"""
TDD Tests for llm.enrich target_schema_path enhancement.

Tests the branch quarantine feature that allows llm.enrich to:
1. Extract a sub-schema at a dot-notation path
2. Extract current data at that path
3. Pass only that branch to the LLM
4. Merge the result back at the correct path

This enables token-efficient, quarantined enrichment of specific schema branches.
"""

import pytest
from core.domains.llm.links import LLMEnrichLink


class TestSchemaPathExtraction:
    """Tests for extracting sub-schemas at dot-notation paths."""
    
    def test_extract_top_level_branch(self):
        """Should extract top-level schema branch."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "morphology": {
                    "type": "object",
                    "properties": {
                        "roots": {"type": "array"},
                        "affixes": {"type": "array"}
                    }
                }
            }
        }
        
        result = LLMEnrichLink._extract_schema_branch(schema, "morphology")
        
        assert result["type"] == "object"
        assert "roots" in result["properties"]
        assert "affixes" in result["properties"]
        assert "name" not in result["properties"]
    
    def test_extract_nested_branch(self):
        """Should extract nested schema branch with dot notation."""
        schema = {
            "type": "object",
            "properties": {
                "morphology": {
                    "type": "object",
                    "properties": {
                        "roots": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "affixes": {"type": "array"}
                    }
                }
            }
        }
        
        result = LLMEnrichLink._extract_schema_branch(schema, "morphology.roots")
        
        assert result["type"] == "array"
        assert result["items"]["type"] == "string"
    
    def test_extract_nonexistent_path(self):
        """Should return None for non-existent paths."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        result = LLMEnrichLink._extract_schema_branch(schema, "nonexistent.path")
        
        assert result is None
    
    def test_extract_empty_path(self):
        """Should return full schema for empty path."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        result = LLMEnrichLink._extract_schema_branch(schema, "")
        
        assert result == schema


class TestDataPathExtraction:
    """Tests for extracting data at dot-notation paths."""
    
    def test_extract_top_level_data(self):
        """Should extract top-level data."""
        data = {
            "name": "test",
            "morphology": {
                "roots": ["root1", "root2"],
                "affixes": []
            }
        }
        
        result = LLMEnrichLink._extract_data_branch(data, "morphology")
        
        assert result == {
            "roots": ["root1", "root2"],
            "affixes": []
        }
    
    def test_extract_nested_data(self):
        """Should extract nested data with dot notation."""
        data = {
            "morphology": {
                "roots": ["root1", "root2"],
                "affixes": []
            }
        }
        
        result = LLMEnrichLink._extract_data_branch(data, "morphology.roots")
        
        assert result == ["root1", "root2"]
    
    def test_extract_nonexistent_path_returns_none(self):
        """Should return None for non-existent paths."""
        data = {
            "name": "test"
        }
        
        result = LLMEnrichLink._extract_data_branch(data, "nonexistent.path")
        
        assert result is None
    
    def test_extract_empty_path(self):
        """Should return full data for empty path."""
        data = {
            "name": "test",
            "value": 123
        }
        
        result = LLMEnrichLink._extract_data_branch(data, "")
        
        assert result == data


class TestDataPathMerge:
    """Tests for merging data back at dot-notation paths."""
    
    def test_merge_top_level(self):
        """Should merge data at top level."""
        data = {
            "name": "test",
            "morphology": {
                "roots": [],
                "affixes": []
            }
        }
        
        new_morphology = {
            "roots": ["new1", "new2"],
            "affixes": [{"affix": "pre-", "type": "prefix"}]
        }
        
        result = LLMEnrichLink._merge_at_path(data, "morphology", new_morphology)
        
        assert result["name"] == "test"
        assert result["morphology"]["roots"] == ["new1", "new2"]
        assert len(result["morphology"]["affixes"]) == 1
    
    def test_merge_nested(self):
        """Should merge data at nested path."""
        data = {
            "morphology": {
                "roots": ["old"],
                "affixes": []
            }
        }
        
        new_roots = ["new1", "new2"]
        
        result = LLMEnrichLink._merge_at_path(data, "morphology.roots", new_roots)
        
        assert result["morphology"]["roots"] == ["new1", "new2"]
        assert result["morphology"]["affixes"] == []
    
    def test_merge_creates_missing_parents(self):
        """Should create missing parent objects when merging."""
        data = {"name": "test"}
        
        new_roots = ["root1"]
        
        result = LLMEnrichLink._merge_at_path(data, "morphology.roots", new_roots)
        
        assert result["name"] == "test"
        assert result["morphology"]["roots"] == ["root1"]
    
    def test_merge_empty_path_replaces_root(self):
        """Should replace entire data for empty path."""
        data = {"old": "value"}
        new_data = {"new": "value"}
        
        result = LLMEnrichLink._merge_at_path(data, "", new_data)
        
        assert result == new_data


class TestBranchQuarantineIntegration:
    """Integration tests for full branch quarantine workflow."""
    
    def test_enrich_with_schema_path(self, mocker):
        """Should quarantine LLM to schema branch when target_schema_path provided."""
        # Mock LLM call
        mock_llm = mocker.patch.object(
            LLMEnrichLink,
            '_call_llm_json_mode',
            return_value={
                "roots": ["vys", "kel"],
                "affixes": [{"affix": "-a", "type": "suffix", "meaning": "plural"}],
                "word_class": "noun"
            }
        )
        
        link_config = {
            "name": "Test Enrich",
            "type": "llm.enrich",
            "document": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "english_word": {"type": "string"},
                        "morphology": {
                            "type": "object",
                            "properties": {
                                "roots": {"type": "array"},
                                "affixes": {"type": "array"},
                                "word_class": {"type": "string"}
                            }
                        }
                    }
                },
                "data": {
                    "english_word": "test",
                    "morphology": {
                        "roots": None,
                        "affixes": None,
                        "word_class": None
                    }
                }
            },
            "source": "The word has roots vys and kel, suffix -a (plural), and is a noun.",
            "target_schema_path": "morphology"
        }
        
        result = LLMEnrichLink.execute(link_config, {})
        
        # Should call LLM with sub-schema only (extracted branch, not wrapped)
        call_args = mock_llm.call_args[1]
        assert "roots" in call_args["schema"]["properties"]
        assert "affixes" in call_args["schema"]["properties"]
        assert "word_class" in call_args["schema"]["properties"]
        assert "english_word" not in call_args["schema"]["properties"]
        assert "morphology" not in call_args["schema"]["properties"]  # Branch extracted, not wrapped
        
        # Should return full document with morphology merged
        assert result["data"]["english_word"] == "test"
        assert result["data"]["morphology"]["roots"] == ["vys", "kel"]
        assert result["data"]["morphology"]["word_class"] == "noun"
    
    def test_backward_compatibility_without_schema_path(self, mocker):
        """Should work normally when target_schema_path not provided."""
        mock_llm = mocker.patch.object(
            LLMEnrichLink,
            '_call_llm_json_mode',
            return_value={
                "english_word": "test",
                "morphology": {"roots": ["test"], "affixes": [], "word_class": "noun"}
            }
        )
        
        link_config = {
            "name": "Test Enrich",
            "type": "llm.enrich",
            "document": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "english_word": {"type": "string"},
                        "morphology": {"type": "object"}
                    }
                },
                "data": {
                    "english_word": None,
                    "morphology": None
                }
            },
            "source": "Test data",
            "target_fields": ["morphology"]
            # No target_schema_path - should use full schema
        }
        
        result = LLMEnrichLink.execute(link_config, {})
        
        # Should call LLM with full schema
        call_args = mock_llm.call_args[1]
        assert "english_word" in call_args["schema"]["properties"]
        assert "morphology" in call_args["schema"]["properties"]


class TestPromptBuilding:
    """Tests for prompt building with schema path quarantine."""
    
    def test_prompt_shows_only_branch_context(self):
        """Should build prompt with only the target branch context."""
        current_data = {
            "roots": None,
            "affixes": None,
            "word_class": None
        }
        
        schema = {
            "type": "object",
            "properties": {
                "roots": {"type": "array"},
                "affixes": {"type": "array"},
                "word_class": {"type": "string"}
            }
        }
        
        prompt = LLMEnrichLink._build_enrichment_prompt(
            current_data=current_data,
            source="Morphological analysis...",
            target_fields=["roots", "affixes", "word_class"],
            schema=schema,
            hint="Extract morphological components"
        )
        
        assert "roots" in prompt
        assert "affixes" in prompt
        assert "word_class" in prompt
        # Should not show fields outside the branch
        assert "english_word" not in prompt
