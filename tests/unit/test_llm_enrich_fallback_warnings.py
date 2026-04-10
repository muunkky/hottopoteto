"""
Tests for warning logging when LLMEnrichLink silently falls back
due to target_schema_path resolving to None.

Covers:
- Schema branch fallback: _extract_schema_branch returns None, execute() falls back to full schema
- Data branch fallback: _extract_data_branch returns None, execute() falls back to {}

Both fallback paths should emit logger.warning() so misconfigured
target_schema_path values are observable instead of silently bypassing quarantine.
"""

import logging
import pytest
from core.domains.llm.links import LLMEnrichLink


class TestSchemaFallbackWarning:
    """Verify warning is logged when schema branch extraction fails."""

    def test_warns_when_schema_branch_not_found(self, mocker, caplog):
        """Should log warning when _extract_schema_branch returns None."""
        mock_llm = mocker.patch.object(
            LLMEnrichLink,
            "_call_llm_json_mode",
            return_value={"english_word": "test"},
        )

        link_config = {
            "name": "Test Enrich",
            "type": "llm.enrich",
            "document": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "english_word": {"type": "string"},
                    },
                },
                "data": {"english_word": None},
            },
            "source": "Some source text",
            "target_schema_path": "nonexistent.branch",
        }

        with caplog.at_level(logging.WARNING, logger="core.domains.llm.links"):
            result = LLMEnrichLink.execute(link_config, {})

        # Should still succeed (fallback behaviour preserved)
        assert "error" not in result.get("data", {})

        # But a warning should have been logged mentioning the bad path
        warning_messages = [
            r.message for r in caplog.records if r.levelno == logging.WARNING
        ]
        schema_warnings = [
            m for m in warning_messages if "nonexistent.branch" in m
        ]
        assert len(schema_warnings) >= 1, (
            f"Expected a warning mentioning 'nonexistent.branch', got: {warning_messages}"
        )


class TestDataFallbackWarning:
    """Verify warning is logged when data branch extraction fails."""

    def test_warns_when_data_branch_not_found(self, mocker, caplog):
        """Should log warning when _extract_data_branch returns None."""
        mock_llm = mocker.patch.object(
            LLMEnrichLink,
            "_call_llm_json_mode",
            return_value={"roots": ["r1"]},
        )

        link_config = {
            "name": "Test Enrich",
            "type": "llm.enrich",
            "document": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "morphology": {
                            "type": "object",
                            "properties": {
                                "roots": {"type": "array"},
                            },
                        },
                    },
                },
                # Schema has the path, but data does NOT
                "data": {"english_word": "test"},
            },
            "source": "Some source text",
            "target_schema_path": "morphology",
        }

        with caplog.at_level(logging.WARNING, logger="core.domains.llm.links"):
            result = LLMEnrichLink.execute(link_config, {})

        assert "error" not in result.get("data", {})

        warning_messages = [
            r.message for r in caplog.records if r.levelno == logging.WARNING
        ]
        data_warnings = [
            m for m in warning_messages if "morphology" in m
        ]
        assert len(data_warnings) >= 1, (
            f"Expected a warning mentioning 'morphology', got: {warning_messages}"
        )


class TestBothFallbackWarnings:
    """Verify both warnings fire when both branches fail to resolve."""

    def test_warns_for_both_schema_and_data_fallback(self, mocker, caplog):
        """Should log warnings for both schema and data branch fallbacks."""
        mock_llm = mocker.patch.object(
            LLMEnrichLink,
            "_call_llm_json_mode",
            return_value={"english_word": "test"},
        )

        link_config = {
            "name": "Test Enrich",
            "type": "llm.enrich",
            "document": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "english_word": {"type": "string"},
                    },
                },
                "data": {"english_word": None},
            },
            "source": "Some source text",
            "target_schema_path": "totally.bogus.path",
        }

        with caplog.at_level(logging.WARNING, logger="core.domains.llm.links"):
            result = LLMEnrichLink.execute(link_config, {})

        warning_messages = [
            r.message for r in caplog.records if r.levelno == logging.WARNING
        ]

        schema_warned = any("schema" in m.lower() and "totally.bogus.path" in m for m in warning_messages)
        data_warned = any("data" in m.lower() and "totally.bogus.path" in m for m in warning_messages)

        assert schema_warned, (
            f"Expected a schema-fallback warning for 'totally.bogus.path', got: {warning_messages}"
        )
        assert data_warned, (
            f"Expected a data-fallback warning for 'totally.bogus.path', got: {warning_messages}"
        )


class TestNoWarningOnValidPath:
    """Verify no spurious warnings when quarantine works correctly."""

    def test_no_warning_when_path_resolves(self, mocker, caplog):
        """Should NOT warn when _extract_schema_branch and _extract_data_branch succeed."""
        mock_llm = mocker.patch.object(
            LLMEnrichLink,
            "_call_llm_json_mode",
            return_value={"roots": ["r1"]},
        )

        link_config = {
            "name": "Test Enrich",
            "type": "llm.enrich",
            "document": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "morphology": {
                            "type": "object",
                            "properties": {
                                "roots": {"type": "array"},
                            },
                        },
                    },
                },
                "data": {
                    "morphology": {"roots": []},
                },
            },
            "source": "Some source text",
            "target_schema_path": "morphology",
        }

        with caplog.at_level(logging.WARNING, logger="core.domains.llm.links"):
            result = LLMEnrichLink.execute(link_config, {})

        fallback_warnings = [
            r.message
            for r in caplog.records
            if r.levelno == logging.WARNING and "fallback" in r.message.lower()
        ]
        assert len(fallback_warnings) == 0, (
            f"Expected no fallback warnings, got: {fallback_warnings}"
        )
