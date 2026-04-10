"""
Spike investigation tests: StorageEntity.tags inheritance under Pydantic v2
Card: TESTCOV1-tt9cb3 (step-4a spike)

These tests document findings from the investigation and serve as a regression
safety net for the step-4b model_fields migration refactor.

Key findings:
1. `tags` field inherits correctly in all GenericEntryModel subclasses
2. `__fields__` == `model_fields` keys for all models (no silent differences)
3. `Word.tags` re-declaration in plugins/conlang is redundant but safe
4. Deprecated: __fields__, .schema(), field_info.allow_none
"""
import pytest
from typing import Optional, List
from pydantic import BaseModel, Field

from core.models import GenericEntryModel
from core.domains.storage.models import StorageEntity, StorageQuery


class TestTagsInheritanceViaModelFields:
    """Verify tags field is correctly inherited through GenericEntryModel subclasses."""

    def test_generic_entry_model_has_tags_in_model_fields(self):
        assert "tags" in GenericEntryModel.model_fields
        fi = GenericEntryModel.model_fields["tags"]
        assert fi.annotation == List[str]
        assert fi.default_factory is list

    def test_storage_entity_inherits_tags_in_model_fields(self):
        """StorageEntity does NOT redeclare tags — should inherit from GenericEntryModel."""
        assert "tags" not in StorageEntity.__annotations__
        assert "tags" in StorageEntity.model_fields
        fi = StorageEntity.model_fields["tags"]
        assert fi.annotation == List[str]
        assert fi.default_factory is list

    def test_storage_entity_tags_default_is_empty_list(self):
        entity = StorageEntity(id="e1", collection="test")
        assert entity.tags == []
        assert isinstance(entity.tags, list)

    def test_storage_entity_tags_accepts_list_of_strings(self):
        entity = StorageEntity(id="e2", collection="test", tags=["a", "b", "c"])
        assert entity.tags == ["a", "b", "c"]

    def test_storage_entity_tags_mutation_does_not_affect_other_instances(self):
        e1 = StorageEntity(id="e1", collection="test")
        e2 = StorageEntity(id="e2", collection="test")
        e1.tags.append("mutated")
        assert e2.tags == []

    def test_subclass_without_tags_redeclaration_inherits_correctly(self):
        """Verify a minimal subclass without re-declaring tags still has it."""

        class MinimalSubclass(GenericEntryModel):
            name: str

        assert "tags" in MinimalSubclass.model_fields
        obj = MinimalSubclass(id="m1", name="test")
        assert obj.tags == []

    def test_subclass_with_tags_redeclaration_still_correct(self):
        """Re-declaring tags identically is redundant but must not break field."""

        class SubclassWithRedeclaredTags(GenericEntryModel):
            name: str
            tags: List[str] = Field(default_factory=list)  # redundant re-declaration

        assert "tags" in SubclassWithRedeclaredTags.model_fields
        fi = SubclassWithRedeclaredTags.model_fields["tags"]
        assert fi.annotation == List[str]
        obj = SubclassWithRedeclaredTags(id="s1", name="test")
        assert obj.tags == []
        obj2 = SubclassWithRedeclaredTags(id="s2", name="test", tags=["x"])
        assert obj2.tags == ["x"]


class TestModelFieldsVsLegacyFields:
    """Verify __fields__ and model_fields return identical field sets."""

    def test_generic_entry_model_fields_keys_match(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            legacy_keys = set(GenericEntryModel.__fields__.keys())
        modern_keys = set(GenericEntryModel.model_fields.keys())
        assert legacy_keys == modern_keys

    def test_storage_entity_fields_keys_match(self):
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            legacy_keys = set(StorageEntity.__fields__.keys())
        modern_keys = set(StorageEntity.model_fields.keys())
        assert legacy_keys == modern_keys

    def test_storage_entity_model_fields_contains_expected_keys(self):
        expected = {"id", "metadata", "created_at", "updated_at", "tags", "collection", "data"}
        assert expected.issubset(set(StorageEntity.model_fields.keys()))


class TestRegistryMethodsUseModelFields:
    """Verify registry lookup keys are correct using model_fields (pre-step-4b migration)."""

    def test_file_adapter_name_accessible_via_model_fields(self):
        """model_fields["name"].default should return "file" for FileAdapter."""
        from core.domains.storage.models import FileAdapter

        name_default = FileAdapter.model_fields["name"].default
        assert name_default == "file"

    def test_openai_provider_name_accessible_via_model_fields(self):
        """model_fields["name"].default should return "openai" for OpenAIProvider."""
        from core.domains.llm.models import OpenAIProvider

        name_default = OpenAIProvider.model_fields["name"].default
        assert name_default == "openai"


class TestDeprecatedApiEmitsWarnings:
    """Document that __fields__ and .schema() emit PydanticDeprecatedSince20 warnings.

    These tests verify the deprecation warnings exist now (pre-migration).
    After step-4b migration, these deprecated calls should not appear in production code.
    """

    def test_fields_access_emits_deprecation_warning(self):
        import warnings
        from pydantic import PydanticDeprecatedSince20

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = StorageEntity.__fields__

        deprecation_warnings = [
            w for w in caught if issubclass(w.category, (DeprecationWarning, PydanticDeprecatedSince20))
        ]
        assert len(deprecation_warnings) >= 1

    def test_schema_method_emits_deprecation_warning(self):
        import warnings
        from pydantic import PydanticDeprecatedSince20

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = StorageEntity.schema()

        deprecation_warnings = [
            w for w in caught if issubclass(w.category, (DeprecationWarning, PydanticDeprecatedSince20))
        ]
        assert len(deprecation_warnings) >= 1

    def test_model_json_schema_does_not_emit_deprecation_warning(self):
        """model_json_schema() is the v2 replacement — should not warn."""
        import warnings
        from pydantic import PydanticDeprecatedSince20

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _ = StorageEntity.model_json_schema()

        deprecation_warnings = [
            w for w in caught
            if issubclass(w.category, (DeprecationWarning, PydanticDeprecatedSince20))
        ]
        assert len(deprecation_warnings) == 0


class TestFieldInfoAttributesInPydanticV2:
    """Document Pydantic v2 FieldInfo attributes relevant to step-4b migration."""

    def test_field_info_has_no_allow_none_attribute(self):
        """FieldInfo in Pydantic v2 does NOT have .allow_none — latent bug in pydantic_integration.py."""

        class SampleModel(BaseModel):
            optional_field: Optional[str] = None

        fi = SampleModel.model_fields["optional_field"]
        assert not hasattr(fi, "allow_none"), (
            "allow_none does not exist in Pydantic v2 FieldInfo — "
            "pydantic_integration.py:43 will raise AttributeError"
        )

    def test_field_info_has_is_required_method(self):
        """is_required() is the correct Pydantic v2 way to check if a field is required."""

        class SampleModel(BaseModel):
            required_field: str
            optional_field: Optional[str] = None
            default_field: str = "hello"
            list_field: List[str] = Field(default_factory=list)

        assert SampleModel.model_fields["required_field"].is_required() is True
        assert SampleModel.model_fields["optional_field"].is_required() is False
        assert SampleModel.model_fields["default_field"].is_required() is False
        assert SampleModel.model_fields["list_field"].is_required() is False
