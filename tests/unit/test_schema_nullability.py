"""
Test that all domain schemas properly allow null for optional fields.

This catches schema design issues before runtime, preventing validation errors
when documents are created with partial data (storage.init with initial_data).
"""
import pytest
from core.registration import get_domain_schema, get_all_domain_schemas


def _load_linguistics_schemas() -> None:
    """Ensure the linguistics domain schemas are registered.

    Registers the stub conlang package in PackageRegistry (if absent) and
    imports the linguistics domain package so that all ``register_domain_schema``
    calls in ``models.py`` are executed.
    """
    if get_domain_schema("linguistics", "word") is not None:
        return  # already loaded

    from core.registry import PackageRegistry
    if "conlang" not in PackageRegistry._packages:
        PackageRegistry.register_package("conlang", None)

    import plugins.conlang.domains.linguistics  # noqa: F401


class TestSchemaNullability:
    """Validate that schemas allow null for optional fields."""

    @pytest.fixture(autouse=True)
    def load_linguistics(self):
        """Load the linguistics plugin schemas before each test in this class."""
        _load_linguistics_schemas()

    def test_linguistics_word_schema_allows_null_for_optional_fields(self):
        """All Optional[List/Dict] fields should allow null in the schema."""
        schema = get_domain_schema("linguistics", "word")
        assert schema is not None, "linguistics.word schema must be registered"

        # Fields that should allow null (Optional fields with default_factory)
        optional_array_fields = [
            "alternate_forms", "origin_words", "irregular_forms", "derived_words",
            "meanings", "semantic_fields", "usage_examples", "collocations",
            "synonyms", "antonyms", "related_words", "compound_of",
            "dialectal_variations", "tags", "cognates", "references"
        ]

        optional_dict_fields = ["metadata"]

        optional_datetime_fields = ["created_at", "updated_at", "created_date", "last_modified"]

        # Check array fields allow null
        for field in optional_array_fields:
            if field in schema["properties"]:
                field_schema = schema["properties"][field]
                assert self._allows_null(field_schema), (
                    f"Field '{field}' should allow null but schema is: {field_schema}"
                )

        # Check dict fields allow null
        for field in optional_dict_fields:
            if field in schema["properties"]:
                field_schema = schema["properties"][field]
                assert self._allows_null(field_schema), (
                    f"Field '{field}' should allow null but schema is: {field_schema}"
                )

        # Check datetime fields allow null
        for field in optional_datetime_fields:
            if field in schema["properties"]:
                field_schema = schema["properties"][field]
                assert self._allows_null(field_schema), (
                    f"Field '{field}' should allow null but schema is: {field_schema}"
                )

    def test_all_domain_schemas_optional_lists_allow_null(self):
        """Generic test: all List fields with default_factory should allow null."""
        all_schemas = get_all_domain_schemas()

        issues = []

        for domain, schemas in all_schemas.items():
            for schema_name, schema in schemas.items():
                if "properties" not in schema:
                    continue

                for field_name, field_schema in schema["properties"].items():
                    # Check if it's an array type
                    if self._is_array_type(field_schema) and not self._allows_null(field_schema):
                        issues.append(f"{domain}.{schema_name}.{field_name}")

        assert not issues, (
            f"These array fields don't allow null but probably should:\n" +
            "\n".join(f"  - {issue}" for issue in issues)
        )

    def _allows_null(self, field_schema: dict) -> bool:
        """Check if a field schema allows null values."""
        # Direct type with null
        if isinstance(field_schema.get("type"), list):
            return "null" in field_schema["type"]

        # anyOf with null option
        if "anyOf" in field_schema:
            for option in field_schema["anyOf"]:
                if option.get("type") == "null":
                    return True

        return False

    def _is_array_type(self, field_schema: dict) -> bool:
        """Check if a field schema is an array type."""
        if field_schema.get("type") == "array":
            return True

        if "anyOf" in field_schema:
            for option in field_schema["anyOf"]:
                if option.get("type") == "array":
                    return True

        return False
