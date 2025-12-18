"""
Unit tests for core.registry module.

Tests the FunctionRegistry and PackageRegistry classes.
"""

import pytest
from core.registry import FunctionRegistry, PackageRegistry


class TestFunctionRegistry:
    """Test suite for FunctionRegistry class."""
    
    def test_registry_exists(self):
        """Test that FunctionRegistry class exists."""
        assert FunctionRegistry is not None
        
    def test_registry_has_register_method(self):
        """Test that FunctionRegistry has a register method."""
        assert hasattr(FunctionRegistry, 'register')
        
    def test_registry_has_get_method(self):
        """Test that FunctionRegistry has a get method."""
        assert hasattr(FunctionRegistry, 'get')
        
    @pytest.mark.skip(reason="Requires function registration implementation details")
    def test_can_register_function(self):
        """Test that functions can be registered."""
        # This will be implemented once we understand the registration API
        pass


class TestPackageRegistry:
    """Test suite for PackageRegistry class."""
    
    def test_registry_exists(self):
        """Test that PackageRegistry class exists."""
        assert PackageRegistry is not None
        
    @pytest.mark.skip(reason="Requires package registration implementation details")
    def test_can_register_package(self):
        """Test that packages can be registered."""
        # This will be implemented once we understand the registration API
        pass
