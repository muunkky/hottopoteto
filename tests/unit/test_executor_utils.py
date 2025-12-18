"""
Comprehensive tests for core.executor module focusing on utility functions.
"""

import pytest
import json
from core.executor import (
    RecipeLinkOutput,
    UserInputOutput,
    LLMOutput,
    FunctionOutput,
    extract_json,
    attempt_fix_truncated_json,
    fix_common_json_errors
)


class TestRecipeLinkOutput:
    """Tests for RecipeLinkOutput base class."""
    
    def test_initialization_with_defaults(self):
        """Test RecipeLinkOutput initializes with default values."""
        output = RecipeLinkOutput()
        
        assert output.raw is None
        assert output.data == {}
    
    def test_initialization_with_values(self):
        """Test RecipeLinkOutput with provided values."""
        output = RecipeLinkOutput(
            raw="test output",
            data={"key": "value"}
        )
        
        assert output.raw == "test output"
        assert output.data == {"key": "value"}
    
    def test_get_data_returns_data_when_present(self):
        """Test get_data() returns structured data when available."""
        output = RecipeLinkOutput(data={"result": "success"})
        
        result = output.get_data()
        
        assert result == {"result": "success"}
    
    def test_get_data_falls_back_to_raw_json(self):
        """Test get_data() parses raw JSON when data is empty."""
        json_str = '{"parsed": "from raw"}'
        output = RecipeLinkOutput(raw=json_str, data={})
        
        result = output.get_data(fallback_to_raw=True)
        
        assert result == {"parsed": "from raw"}
    
    def test_get_data_wraps_unparseable_raw(self):
        """Test get_data() wraps unparseable raw content."""
        output = RecipeLinkOutput(raw="plain text", data={})
        
        result = output.get_data(fallback_to_raw=True)
        
        assert result == {"raw_content": "plain text"}
    
    def test_get_data_returns_empty_when_no_fallback(self):
        """Test get_data() returns empty dict when fallback disabled."""
        output = RecipeLinkOutput(raw="content", data={})
        
        result = output.get_data(fallback_to_raw=False)
        
        assert result == {}
    
    def test_get_data_prefers_data_over_raw(self):
        """Test that data is preferred even when raw is present."""
        output = RecipeLinkOutput(
            raw='{"raw": "value"}',
            data={"data": "value"}
        )
        
        result = output.get_data()
        
        assert result == {"data": "value"}


class TestOutputSubclasses:
    """Tests for output subclasses."""
    
    def test_user_input_output_inherits_correctly(self):
        """Test UserInputOutput inherits from RecipeLinkOutput."""
        output = UserInputOutput(raw="user input", data={"input": "test"})
        
        assert isinstance(output, RecipeLinkOutput)
        assert output.raw == "user input"
        assert output.data == {"input": "test"}
    
    def test_llm_output_inherits_correctly(self):
        """Test LLMOutput inherits from RecipeLinkOutput."""
        output = LLMOutput(raw="llm response", data={"response": "AI answer"})
        
        assert isinstance(output, RecipeLinkOutput)
        assert output.raw == "llm response"
    
    def test_function_output_inherits_correctly(self):
        """Test FunctionOutput inherits from RecipeLinkOutput."""
        output = FunctionOutput(raw="function result", data={"result": 42})
        
        assert isinstance(output, RecipeLinkOutput)
        assert output.data == {"result": 42}


class TestExtractJson:
    """Tests for extract_json utility function."""
    
    def test_extract_from_dict(self):
        """Test extracting JSON from a dictionary."""
        input_dict = {"key": "value", "number": 42}
        result = extract_json(input_dict)
        
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == input_dict
    
    def test_extract_from_clean_json_string(self):
        """Test extracting from clean JSON string."""
        json_str = '{"name": "test", "value": 123}'
        result = extract_json(json_str)
        
        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["value"] == 123
    
    def test_extract_from_text_with_embedded_json(self):
        """Test extracting JSON embedded in text."""
        text = 'Here is some JSON: {"data": "embedded", "count": 5} and more text'
        result = extract_json(text)
        
        parsed = json.loads(result)
        assert "data" in parsed or isinstance(parsed, dict)
    
    def test_extract_from_markdown_code_block(self):
        """Test extracting JSON from markdown code block."""
        text = '''Some preamble
```json
{"markdown": "block", "value": 42}
```
Some postamble'''
        result = extract_json(text)
        
        parsed = json.loads(result)
        assert "markdown" in parsed or "value" in parsed


class TestAttemptFixTruncatedJson:
    """Tests for attempt_fix_truncated_json function."""
    
    def test_adds_missing_closing_brace(self):
        """Test that missing closing braces are added."""
        truncated = '{"key": "value", "nested": {"inner": "data"'
        result = attempt_fix_truncated_json(truncated)
        
        # Should be parseable now
        parsed = json.loads(result)
        assert "key" in parsed
    
    def test_handles_completely_closed_json(self):
        """Test that already-valid JSON passes through."""
        valid = '{"key": "value", "other": {"nested": "data"}}'
        result = attempt_fix_truncated_json(valid)
        
        parsed = json.loads(result)
        assert parsed["key"] == "value"
    
    def test_handles_no_opening_brace(self):
        """Test handling text without opening brace."""
        text = "no json here at all"
        result = attempt_fix_truncated_json(text)
        
        # Should return input unchanged
        assert text in result
    
    def test_handles_multiple_missing_braces(self):
        """Test handling multiple levels of missing closing braces."""
        truncated = '{"level1": {"level2": {"level3": "value"'
        result = attempt_fix_truncated_json(truncated)
        
        # Should add all missing braces
        parsed = json.loads(result)
        assert parsed["level1"]["level2"]["level3"] == "value"


class TestFixCommonJsonErrors:
    """Tests for fix_common_json_errors function."""
    
    def test_fixes_trailing_commas(self):
        """Test that trailing commas are removed."""
        bad_json = '{"key": "value", "other": "data",}'
        fixed = fix_common_json_errors(bad_json)
        
        parsed = json.loads(fixed)
        assert parsed["key"] == "value"
    
    def test_fixes_unquoted_keys(self):
        """Test that unquoted keys get quoted."""
        bad_json = '{key: "value", other: "data"}'
        fixed = fix_common_json_errors(bad_json)
        
        parsed = json.loads(fixed)
        assert "key" in parsed
    
    def test_removes_javascript_line_comments(self):
        """Test that // comments are removed."""
        bad_json = '''{"key": "value", // this is a comment
"other": "data"}'''
        fixed = fix_common_json_errors(bad_json)
        
        parsed = json.loads(fixed)
        assert parsed["key"] == "value"
    
    def test_removes_javascript_block_comments(self):
        """Test that /* */ comments are removed."""
        bad_json = '{"key": /* comment */ "value"}'
        fixed = fix_common_json_errors(bad_json)
        
        parsed = json.loads(fixed)
        assert parsed["key"] == "value"
    
    def test_handles_already_valid_json(self):
        """Test that valid JSON passes through unchanged."""
        valid_json = '{"key": "value", "number": 42, "bool": true}'
        fixed = fix_common_json_errors(valid_json)
        
        parsed = json.loads(fixed)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42
