"""
Integration tests for Eldorian Word Recipe v2 - Schema-Driven Document Enrichment.

These tests verify that the enhanced eldorian_word_v2.yaml recipe correctly uses
the new DOCENRICH link types (storage.init, storage.update, llm.extract_to_schema,
llm.enrich) to progressively build schema-validated word entries.

Test Strategy:
1. Validate recipe YAML syntax and structure
2. Verify link configurations match expected patterns
3. Mock LLM calls to test workflow integration
4. Validate output schema compliance
"""

import pytest
import yaml
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def recipe_path():
    """Path to the enhanced recipe file."""
    return Path(__file__).parent.parent.parent / "templates" / "recipes" / "conlang" / "eldorian_word_v2.yaml"


@pytest.fixture
def schema_path():
    """Path to the eldorian word schema file."""
    return Path(__file__).parent.parent.parent / "templates" / "schemas" / "conlang" / "eldorian_word.yaml"


@pytest.fixture
def recipe(recipe_path):
    """Load the recipe YAML."""
    with open(recipe_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def schema(schema_path):
    """Load the schema YAML."""
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


# =============================================================================
# Recipe Structure Tests
# =============================================================================

class TestRecipeStructure:
    """Tests for recipe YAML structure and validity."""
    
    def test_recipe_file_exists(self, recipe_path):
        """Recipe file should exist."""
        assert recipe_path.exists(), f"Recipe file not found: {recipe_path}"
    
    def test_schema_file_exists(self, schema_path):
        """Schema file should exist."""
        assert schema_path.exists(), f"Schema file not found: {schema_path}"
    
    def test_recipe_has_required_fields(self, recipe):
        """Recipe should have required top-level fields."""
        assert "name" in recipe
        assert "version" in recipe
        assert "links" in recipe
        assert recipe["version"] == "2.1"
    
    def test_recipe_has_links(self, recipe):
        """Recipe should contain links array."""
        assert isinstance(recipe["links"], list)
        assert len(recipe["links"]) > 0


# =============================================================================
# DOCENRICH Link Type Tests
# =============================================================================

class TestStorageInitLink:
    """Tests for storage.init link configuration."""
    
    def test_has_storage_init_link(self, recipe):
        """Recipe should have a storage.init link."""
        init_links = [l for l in recipe["links"] if l.get("type") == "storage.init"]
        assert len(init_links) >= 1, "Recipe should have at least one storage.init link"
    
    def test_storage_init_uses_schema_ref(self, recipe):
        """storage.init link should reference domain schema via $ref."""
        init_link = next(l for l in recipe["links"] if l.get("type") == "storage.init")
        assert "schema" in init_link
        # New architecture uses $ref to domain schema instead of file reference
        assert "$ref" in init_link["schema"]
        assert init_link["schema"]["$ref"] == "linguistics.word"
    
    def test_storage_init_has_collection(self, recipe):
        """storage.init link should specify collection."""
        init_link = next(l for l in recipe["links"] if l.get("type") == "storage.init")
        assert "collection" in init_link
        assert init_link["collection"] == "eldorian_words"
    
    def test_storage_init_has_initial_data(self, recipe):
        """storage.init link should have initial_data."""
        init_link = next(l for l in recipe["links"] if l.get("type") == "storage.init")
        assert "initial_data" in init_link
        assert "english_word" in init_link["initial_data"]
        assert "connotation" in init_link["initial_data"]


class TestLLMExtractToSchemaLink:
    """Tests for llm.extract_to_schema link configuration."""
    
    def test_has_extract_to_schema_link(self, recipe):
        """Recipe should have at least one llm.extract_to_schema link."""
        extract_links = [l for l in recipe["links"] if l.get("type") == "llm.extract_to_schema"]
        assert len(extract_links) >= 1, "Recipe should have at least one llm.extract_to_schema link"
    
    def test_extract_link_has_source(self, recipe):
        """llm.extract_to_schema link should have source."""
        extract_link = next(l for l in recipe["links"] if l.get("type") == "llm.extract_to_schema")
        assert "source" in extract_link
    
    def test_extract_link_has_schema(self, recipe):
        """llm.extract_to_schema link should have schema."""
        extract_link = next(l for l in recipe["links"] if l.get("type") == "llm.extract_to_schema")
        assert "schema" in extract_link
    
    def test_extract_link_has_hint(self, recipe):
        """llm.extract_to_schema link should have hint for guidance."""
        extract_link = next(l for l in recipe["links"] if l.get("type") == "llm.extract_to_schema")
        assert "hint" in extract_link


class TestLLMEnrichLink:
    """Tests for llm.enrich link configuration."""
    
    def test_has_enrich_links(self, recipe):
        """Recipe should have llm.enrich links."""
        enrich_links = [l for l in recipe["links"] if l.get("type") == "llm.enrich"]
        assert len(enrich_links) >= 1, "Recipe should have at least one llm.enrich link"
    
    def test_enrich_links_have_document(self, recipe):
        """llm.enrich links should have document reference."""
        enrich_links = [l for l in recipe["links"] if l.get("type") == "llm.enrich"]
        for link in enrich_links:
            assert "document" in link, f"Enrich link '{link.get('name')}' missing document"
    
    def test_enrich_links_have_source(self, recipe):
        """llm.enrich links should have source."""
        enrich_links = [l for l in recipe["links"] if l.get("type") == "llm.enrich"]
        for link in enrich_links:
            assert "source" in link, f"Enrich link '{link.get('name')}' missing source"
    
    def test_enrich_links_have_target_fields(self, recipe):
        """llm.enrich links should have target_fields or target_schema_path."""
        enrich_links = [l for l in recipe["links"] if l.get("type") == "llm.enrich"]
        for link in enrich_links:
            has_target_fields = "target_fields" in link
            has_target_schema_path = "target_schema_path" in link
            assert has_target_fields or has_target_schema_path, \
                f"Enrich link '{link.get('name')}' missing target_fields or target_schema_path"
            
            # If has target_fields, should be a list
            if has_target_fields:
                assert isinstance(link["target_fields"], list)


class TestStorageUpdateLink:
    """Tests for storage.update link configuration."""
    
    def test_has_storage_update_links(self, recipe):
        """Recipe should have storage.update links."""
        update_links = [l for l in recipe["links"] if l.get("type") == "storage.update"]
        assert len(update_links) >= 1, "Recipe should have at least one storage.update link"
    
    def test_update_links_have_document_id(self, recipe):
        """storage.update links should reference document_id."""
        update_links = [l for l in recipe["links"] if l.get("type") == "storage.update"]
        for link in update_links:
            assert "document_id" in link, f"Update link '{link.get('name')}' missing document_id"
    
    def test_update_links_have_collection(self, recipe):
        """storage.update links should specify collection."""
        update_links = [l for l in recipe["links"] if l.get("type") == "storage.update"]
        for link in update_links:
            assert "collection" in link, f"Update link '{link.get('name')}' missing collection"
    
    def test_update_links_have_data(self, recipe):
        """storage.update links should have data to merge."""
        update_links = [l for l in recipe["links"] if l.get("type") == "storage.update"]
        for link in update_links:
            assert "data" in link, f"Update link '{link.get('name')}' missing data"


# =============================================================================
# Workflow Pattern Tests
# =============================================================================

class TestDocenrichPattern:
    """Tests verifying the DOCENRICH workflow pattern is implemented correctly."""
    
    def test_init_comes_early(self, recipe):
        """storage.init should come early in the recipe."""
        link_names = [l.get("name") for l in recipe["links"]]
        init_index = next(i for i, l in enumerate(recipe["links"]) if l.get("type") == "storage.init")
        # storage.init should be in first 3 links (after user_input)
        assert init_index <= 2, "storage.init should be near the beginning of the recipe"
    
    def test_progressive_updates(self, recipe):
        """Recipe should have multiple storage.update links for progressive building."""
        update_links = [l for l in recipe["links"] if l.get("type") == "storage.update"]
        assert len(update_links) >= 3, "Recipe should have at least 3 storage.update links for progressive building"
    
    def test_two_step_pattern_for_origins(self, recipe):
        """Origins should follow two-step pattern: llm → extract."""
        link_names = [l.get("name") for l in recipe["links"]]
        
        # Find the sequence - origins use generate → extract pattern
        # (no separate Update with Origins - data flows directly to next phase)
        assert "Generate the Origin Words" in link_names
        assert "Extract Origin Words" in link_names
        
        # Verify order
        gen_idx = link_names.index("Generate the Origin Words")
        extract_idx = link_names.index("Extract Origin Words")
        
        assert gen_idx < extract_idx
    
    def test_two_step_pattern_for_morphology(self, recipe):
        """Morphology should follow two-step pattern: llm → enrich → update."""
        link_names = [l.get("name") for l in recipe["links"]]
        
        assert "Apply Morphology" in link_names
        assert "Enrich Morphology" in link_names
        assert "Update with Morphology" in link_names
        
        morph_idx = link_names.index("Apply Morphology")
        enrich_idx = link_names.index("Enrich Morphology")
        update_idx = link_names.index("Update with Morphology")
        
        assert morph_idx < enrich_idx < update_idx
    
    def test_two_step_pattern_for_phonology(self, recipe):
        """Phonology should follow two-step pattern: llm → enrich → update."""
        link_names = [l.get("name") for l in recipe["links"]]
        
        assert "Apply Phonology" in link_names
        assert "Enrich Phonology" in link_names
        assert "Update with Phonology" in link_names


# =============================================================================
# Schema Compliance Tests
# =============================================================================

class TestSchemaCompliance:
    """Tests verifying recipe output aligns with schema."""
    
    def test_schema_has_required_fields(self, schema):
        """Schema should define required fields."""
        assert "required" in schema
        assert "english_word" in schema["required"]
        assert "eldorian_word" in schema["required"]
    
    def test_schema_has_origin_words(self, schema):
        """Schema should define origin_words array."""
        assert "origin_words" in schema["properties"]
        assert schema["properties"]["origin_words"]["type"] == "array"
    
    def test_schema_has_morphology(self, schema):
        """Schema should define morphology object."""
        assert "morphology" in schema["properties"]
        assert schema["properties"]["morphology"]["type"] == "object"
    
    def test_schema_has_usage_examples(self, schema):
        """Schema should define usage_examples array."""
        assert "usage_examples" in schema["properties"]
        assert schema["properties"]["usage_examples"]["type"] == "array"
    
    def test_schema_has_cultural_notes(self, schema):
        """Schema should define cultural_notes field."""
        assert "cultural_notes" in schema["properties"]
        assert schema["properties"]["cultural_notes"]["type"] == "string"


# =============================================================================
# New Features Tests
# =============================================================================

class TestNewFeatures:
    """Tests for new features in v2 recipe."""
    
    def test_has_cultural_context_generation(self, recipe):
        """Recipe should generate cultural context."""
        link_names = [l.get("name") for l in recipe["links"]]
        assert "Generate Cultural Context" in link_names
    
    def test_has_pronunciation_in_output(self, recipe):
        """Recipe should have final word in generation_summary."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        # v2.1 uses word + generation_log_id + generation_summary architecture
        assert "generation_summary" in save_link["data"]
        assert "final_word" in save_link["data"]["generation_summary"]
    
    def test_has_usage_examples_in_output(self, recipe):
        """Recipe should capture word object with enriched data."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        # v2.1 saves the enriched word from Update_with_Cultural_Context
        assert "word" in save_link["data"]
    
    def test_has_cultural_notes_in_output(self, recipe):
        """Recipe should capture cultural context via the word object."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        # The word object comes from Update_with_Cultural_Context which includes cultural data
        assert "word" in save_link["data"]
    
    def test_has_working_document_reference(self, recipe):
        """Final save should include generation log ID for traceability."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        assert "generation_log_id" in save_link["data"]
    
    def test_metadata_includes_word_id(self, recipe):
        """Metadata should reference word document ID."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        assert "metadata" in save_link
        assert "word_id" in save_link["metadata"]


# =============================================================================
# Backward Compatibility Tests
# =============================================================================

class TestBackwardCompatibility:
    """Tests ensuring backward compatibility with v1 recipe outputs."""
    
    def test_has_storage_save(self, recipe):
        """Recipe should still use storage.save for final persistence."""
        save_links = [l for l in recipe["links"] if l.get("type") == "storage.save"]
        assert len(save_links) >= 1
    
    def test_save_has_core_fields(self, recipe):
        """Final save should include word, generation_log_id, and generation_summary (v2.1 clean architecture)."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        
        # v2.1 uses clean architecture: word object + generation log reference + summary
        required_fields = [
            "word",                # The canonical linguistics.word object
            "generation_log_id",   # Reference to separate generation log document
            "generation_summary"   # Quick reference summary
        ]
        
        for field in required_fields:
            assert field in save_link["data"], f"Missing required field: {field}"
        
        # Verify generation_summary has expected fields
        summary = save_link["data"]["generation_summary"]
        assert "origin_language" in save_link["data"]["generation_summary"]
        assert "final_word" in save_link["data"]["generation_summary"]
    
    def test_preserves_original_links(self, recipe):
        """Recipe should preserve key original LLM links."""
        link_names = [l.get("name") for l in recipe["links"]]
        
        original_links = [
            "Initial User Inputs",
            "Clarify Instructions",
            "Selecting an Origin Language",
            "Generate the Origin Words",
            "Apply Morphology",
            "Apply Phonology",
            "Generate Derivatives"
        ]
        
        for link_name in original_links:
            assert link_name in link_names, f"Missing original link: {link_name}"
