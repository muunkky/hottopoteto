"""
Integration test to validate eldorian_word_v2 recipe produces output
matching the master output schema.

This test validates that the comprehensive output structure defined in
eldorian_word_master_output.yaml matches what the recipe will produce.
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def recipe_path():
    """Path to the recipe file."""
    return Path(__file__).parent.parent.parent / "templates" / "recipes" / "conlang" / "eldorian_word_v2.yaml"


@pytest.fixture
def master_schema_path():
    """Path to the master output schema file."""
    return Path(__file__).parent.parent.parent / "templates" / "schemas" / "conlang" / "eldorian_word_master_output.yaml"


@pytest.fixture
def recipe(recipe_path):
    """Load the recipe YAML."""
    with open(recipe_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.fixture
def master_schema(master_schema_path):
    """Load the master output schema YAML."""
    with open(master_schema_path, 'r') as f:
        return yaml.safe_load(f)


class TestMasterOutputSchema:
    """Tests validating recipe output against master schema."""
    
    def test_master_schema_file_exists(self, master_schema_path):
        """Master output schema file should exist."""
        assert master_schema_path.exists(), f"Master schema not found: {master_schema_path}"
    
    def test_recipe_references_master_schema(self, recipe):
        """Recipe's storage.save should reference master output schema."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        assert "schema" in save_link, "storage.save missing schema configuration"
        assert "file" in save_link["schema"], "storage.save schema missing file reference"
        assert "eldorian_word_master_output.yaml" in save_link["schema"]["file"]
    
    def test_master_schema_has_required_fields(self, master_schema):
        """Master schema should define all required top-level fields."""
        required_fields = [
            "Initial_User_Inputs",
            "Clarify_Instructions",
            "Selecting_an_Origin_Language",
            "Choose_number_of_origin_words",
            "Generate_the_Origin_Words",
            "Apply_Morphology",
            "Generate_Derivatives"
        ]
        
        assert "required" in master_schema, "Master schema missing required array"
        for field in required_fields:
            assert field in master_schema["required"], f"Master schema missing required field: {field}"
    
    def test_recipe_output_matches_master_schema_fields(self, recipe, master_schema):
        """Recipe storage.save data should match master schema properties."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        save_data_fields = save_link["data"].keys()
        schema_properties = master_schema["properties"].keys()
        
        # All data fields should be in schema
        for field in save_data_fields:
            assert field in schema_properties, \
                f"Recipe outputs '{field}' but master schema doesn't define it"
    
    def test_clarify_instructions_has_output_schema(self, recipe):
        """Clarify Instructions link should have output_schema for structured data."""
        clarify_link = next(l for l in recipe["links"] if l.get("name") == "Clarify Instructions")
        assert "output_schema" in clarify_link, \
            "Clarify Instructions missing output_schema - would produce unstructured data"
        assert "raw_content" in clarify_link["output_schema"]["properties"], \
            "Clarify Instructions output_schema should define raw_content field"
    
    def test_initial_user_inputs_structure(self, master_schema):
        """Initial_User_Inputs should have expected structure."""
        initial_inputs = master_schema["properties"]["Initial_User_Inputs"]
        assert initial_inputs["type"] == "object"
        assert "english_word" in initial_inputs["properties"]
        assert "connotation" in initial_inputs["properties"]
        assert "base_form" in initial_inputs["properties"]
    
    def test_generate_origin_words_structure(self, master_schema):
        """Generate_the_Origin_Words should have expected structure."""
        origin_words = master_schema["properties"]["Generate_the_Origin_Words"]
        assert origin_words["type"] == "object"
        assert "compound_origin_word" in origin_words["properties"]
        assert "revised_connotation" in origin_words["properties"]
        assert "origin_words" in origin_words["properties"]
        assert origin_words["properties"]["origin_words"]["type"] == "array"
    
    def test_apply_morphology_structure(self, master_schema):
        """Apply_Morphology should have expected structure."""
        morphology = master_schema["properties"]["Apply_Morphology"]
        assert morphology["type"] == "object"
        assert "morphology" in morphology["properties"]
        assert "updated_word" in morphology["properties"]
    
    def test_generate_derivatives_structure(self, master_schema):
        """Generate_Derivatives should have expected structure."""
        derivatives = master_schema["properties"]["Generate_Derivatives"]
        assert derivatives["type"] == "object"
        assert "base_word" in derivatives["properties"]
        assert "english_word" in derivatives["properties"]
        assert "derivatives" in derivatives["properties"]
        assert derivatives["properties"]["derivatives"]["type"] == "array"
    
    def test_final_word_entry_and_working_doc_id(self, recipe):
        """Recipe should output final_word_entry and working_document_id."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        assert "final_word_entry" in save_link["data"]
        assert "working_document_id" in save_link["data"]
    
    def test_template_paths_use_text_directory(self, recipe):
        """All template file references should include text/ prefix."""
        template_links = [l for l in recipe["links"] if "template" in l and isinstance(l["template"], dict)]
        
        for link in template_links:
            if "file" in link["template"]:
                template_file = link["template"]["file"]
                assert template_file.startswith("text/"), \
                    f"Link '{link.get('name')}' template path missing text/ prefix: {template_file}"
    
    def test_storage_save_data_not_double_nested(self, recipe):
        """Storage.save final_word_entry should be .data not .data.data."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        final_word_entry = save_link["data"]["final_word_entry"]
        
        # Should reference Update_with_Cultural_Context.data (not .data.data)
        assert "Update_with_Cultural_Context.data" in final_word_entry, \
            "final_word_entry should use .data reference"
        assert "Update_with_Cultural_Context.data.data" not in final_word_entry, \
            "final_word_entry should NOT have double .data.data nesting"
    
    def test_comprehensive_output_includes_all_phases(self, recipe):
        """Comprehensive output should capture all 7 processing phases."""
        save_link = next(l for l in recipe["links"] if l.get("type") == "storage.save")
        
        # All 7 phases should be in output
        phases = [
            "Initial_User_Inputs",           # Phase 1
            "Clarify_Instructions",          # Phase 2
            "Selecting_an_Origin_Language",  # Phase 2
            "Choose_number_of_origin_words", # Phase 2
            "Target_number_of_syllables",    # Phase 2
            "Generate_the_Origin_Words",     # Phase 2
            "Apply_Morphology",              # Phase 4
            "Apply_Phonology",               # Phase 5
            "Generate_Derivatives",          # Phase 6
            "Generate_Cultural_Context",     # Phase 6
        ]
        
        for phase in phases:
            assert phase in save_link["data"], f"Output missing phase: {phase}"
