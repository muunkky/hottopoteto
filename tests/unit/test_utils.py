"""Tests for core.utils module."""
import pytest
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from core.utils import (
    ensure_directory,
    generate_id,
    safe_load_json,
    safe_save_json,
    format_timestamp
)


class TestEnsureDirectory:
    """Tests for ensure_directory function."""
    
    def test_creates_directory(self, tmp_path):
        """Test that directory is created."""
        test_dir = tmp_path / "new_directory"
        
        result = ensure_directory(str(test_dir))
        
        assert result is True
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_handles_existing_directory(self, tmp_path):
        """Test that existing directory doesn't cause error."""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()
        
        result = ensure_directory(str(test_dir))
        
        assert result is True
        assert test_dir.exists()
    
    def test_creates_nested_directories(self, tmp_path):
        """Test creating nested directory structure."""
        test_dir = tmp_path / "level1" / "level2" / "level3"
        
        result = ensure_directory(str(test_dir))
        
        assert result is True
        assert test_dir.exists()


class TestGenerateId:
    """Tests for generate_id function."""
    
    def test_generates_id_without_prefix(self):
        """Test generating ID without prefix."""
        id1 = generate_id()
        
        assert isinstance(id1, str)
        assert len(id1) == 8  # UUID hex[:8]
    
    def test_generates_id_with_prefix(self):
        """Test generating ID with prefix."""
        id1 = generate_id(prefix="test")
        
        assert id1.startswith("test-")
        assert len(id1) == 13  # "test-" + 8 chars
    
    def test_generates_unique_ids(self):
        """Test that generated IDs are unique."""
        ids = [generate_id() for _ in range(100)]
        
        assert len(set(ids)) == 100  # All unique
    
    def test_prefix_is_lowercased(self):
        """Test that prefix is converted to lowercase."""
        id1 = generate_id(prefix="TEST")
        
        assert id1.startswith("test-")


class TestSafeLoadJson:
    """Tests for safe_load_json function."""
    
    def test_loads_valid_json_file(self, tmp_path):
        """Test loading a valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))
        
        result = safe_load_json(str(test_file))
        
        assert result == test_data
    
    def test_returns_default_for_missing_file(self):
        """Test that default is returned for missing file."""
        result = safe_load_json("/nonexistent/file.json", default={"default": True})
        
        assert result == {"default": True}
    
    def test_returns_empty_dict_by_default(self):
        """Test that empty dict is default when not specified."""
        result = safe_load_json("/nonexistent/file.json")
        
        assert result == {}
    
    def test_handles_invalid_json(self, tmp_path):
        """Test handling of invalid JSON content."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{ invalid json }")
        
        result = safe_load_json(str(test_file), default={"error": "fallback"})
        
        assert result == {"error": "fallback"}


class TestSafeSaveJson:
    """Tests for safe_save_json function."""
    
    def test_saves_json_file(self, tmp_path):
        """Test saving data to JSON file."""
        test_file = tmp_path / "output.json"
        test_data = {"saved": True, "value": 123}
        
        result = safe_save_json(str(test_file), test_data)
        
        assert result is True
        assert test_file.exists()
        
        loaded = json.loads(test_file.read_text())
        assert loaded == test_data
    
    def test_creates_directory_if_needed(self, tmp_path):
        """Test that parent directories are created."""
        test_file = tmp_path / "nested" / "path" / "data.json"
        test_data = {"nested": "save"}
        
        result = safe_save_json(str(test_file), test_data)
        
        assert result is True
        assert test_file.exists()
    
    def test_uses_custom_indent(self, tmp_path):
        """Test that custom indentation is applied."""
        test_file = tmp_path / "indented.json"
        test_data = {"key": "value"}
        
        safe_save_json(str(test_file), test_data, indent=4)
        
        content = test_file.read_text()
        assert "    " in content  # 4-space indent
    
    def test_preserves_unicode(self, tmp_path):
        """Test that Unicode characters are preserved."""
        test_file = tmp_path / "unicode.json"
        test_data = {"text": "Hello 世界", "emoji": "🎉"}
        
        safe_save_json(str(test_file), test_data)
        
        loaded = json.loads(test_file.read_text(encoding="utf-8"))
        assert loaded["text"] == "Hello 世界"
        assert loaded["emoji"] == "🎉"


class TestFormatTimestamp:
    """Tests for format_timestamp function."""
    
    def test_formats_current_time_when_none(self):
        """Test formatting current time when no timestamp provided."""
        result = format_timestamp()
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_formats_datetime_object(self):
        """Test formatting a datetime object."""
        dt = datetime(2025, 12, 18, 15, 30, 45)
        result = format_timestamp(dt)
        
        assert isinstance(result, str)
        assert "2025" in result
    
    def test_formats_string_timestamp(self):
        """Test formatting a string timestamp."""
        timestamp_str = "2025-12-18T15:30:45"
        result = format_timestamp(timestamp_str)
        
        assert isinstance(result, str)
