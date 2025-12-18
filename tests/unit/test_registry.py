"""
Unit tests for core.registry module.

Tests the FunctionRegistry and PackageRegistry classes.
"""

import pytest
from types import ModuleType
from core.registry import FunctionRegistry, PackageRegistry


class TestFunctionRegistry:
    """Test suite for FunctionRegistry class."""
    
    def setup_method(self):
        """Clear registry before each test."""
        FunctionRegistry._functions.clear()
    
    def test_registry_exists(self):
        """Test that FunctionRegistry class exists."""
        assert FunctionRegistry is not None
        
    def test_registry_has_register_method(self):
        """Test that FunctionRegistry has a register method."""
        assert hasattr(FunctionRegistry, 'register')
        
    def test_registry_has_get_method(self):
        """Test that FunctionRegistry has a get method."""
        assert hasattr(FunctionRegistry, 'get')
    
    def test_can_register_function(self):
        """Test that functions can be registered."""
        def test_func():
            return "test result"
        
        FunctionRegistry.register("test_function", test_func)
        
        assert "test_function" in FunctionRegistry._functions
        assert FunctionRegistry._functions["test_function"]["function"] == test_func
    
    def test_can_get_registered_function(self):
        """Test retrieving a registered function."""
        def my_func():
            return 42
        
        FunctionRegistry.register("my_function", my_func)
        result = FunctionRegistry.get("my_function")
        
        assert result == my_func
        assert result() == 42
    
    def test_get_nonexistent_returns_none(self):
        """Test getting non-existent function returns None."""
        result = FunctionRegistry.get("nonexistent")
        assert result is None
    
    def test_register_with_metadata(self):
        """Test registering function with metadata."""
        def test_func():
            return "test"
        
        metadata = {"description": "Test function"}
        FunctionRegistry.register("test_meta", test_func, meta=metadata)
        
        assert FunctionRegistry._functions["test_meta"]["metadata"] == metadata


class TestPackageRegistry:
    """Test suite for PackageRegistry class."""
    
    def setup_method(self):
        """Clear registry before each test."""
        PackageRegistry._packages.clear()
        PackageRegistry._domains.clear()
        PackageRegistry._plugins.clear()
        PackageRegistry._core_package = None
    
    def test_registry_exists(self):
        """Test that PackageRegistry class exists."""
        assert PackageRegistry is not None
    
    def test_can_register_core_package(self):
        """Test registering the core package."""
        core_module = ModuleType("core")
        core_module.__version__ = "1.0.0"
        
        PackageRegistry.register_core_package(core_module)
        
        assert PackageRegistry._core_package == core_module
        assert "core" in PackageRegistry._packages
        assert PackageRegistry._packages["core"]["type"] == "core"
    
    def test_can_register_extension_package(self):
        """Test that extension packages can be registered."""
        ext_module = ModuleType("my_extension")
        ext_module.__version__ = "2.0.0"
        
        PackageRegistry.register_package("my_extension", ext_module)
        
        assert "my_extension" in PackageRegistry._packages
        assert PackageRegistry._packages["my_extension"]["type"] == "extension"
    
    def test_is_core_package_check(self):
        """Test checking if package is core."""
        core_module = ModuleType("core")
        PackageRegistry.register_core_package(core_module)
        
        assert PackageRegistry.is_core_package("core") is True
        assert PackageRegistry.is_core_package("other") is False

