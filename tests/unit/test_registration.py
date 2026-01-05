"""Tests for core.registration.domains module."""
import pytest
from core.registration.domains import (
    register_domain_interface,
    register_package_for_domain,
    get_packages_for_domain,
    get_domain_interface,
    list_domains,
    register_domain_schema,
    register_domain_function,
    get_domain_function,
    _domain_interfaces,
    _domain_packages
)


class TestDomainInterfaceRegistration:
    """Tests for domain interface registration."""
    
    def setup_method(self):
        """Clear registries before each test."""
        _domain_interfaces.clear()
        _domain_packages.clear()
    
    def test_register_domain_interface(self):
        """Test registering a domain interface."""
        interface_data = {
            "name": "test",
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        }
        
        register_domain_interface("test", interface_data)
        
        assert "test" in _domain_interfaces
        assert _domain_interfaces["test"] == interface_data
    
    def test_get_domain_interface(self):
        """Test retrieving registered domain interface."""
        interface_data = {"name": "test", "version": "1.0.0"}
        register_domain_interface("test", interface_data)
        
        result = get_domain_interface("test")
        
        assert result == interface_data
    
    def test_get_domain_interface_returns_none_for_unregistered(self):
        """Test getting unregistered interface returns None."""
        result = get_domain_interface("nonexistent")
        assert result is None
    
    def test_list_domains_returns_registered_names(self):
        """Test listing all registered domains."""
        register_domain_interface("domain1", {"name": "domain1"})
        register_domain_interface("domain2", {"name": "domain2"})
        
        domains = list_domains()
        
        assert "domain1" in domains
        assert "domain2" in domains


class TestPackageRegistration:
    """Tests for package-domain association."""
    
    def setup_method(self):
        """Clear registries before each test."""
        _domain_interfaces.clear()
        _domain_packages.clear()
    
    def test_register_package_for_domain(self):
        """Test registering a package for a domain."""
        register_domain_interface("test", {"name": "test"})
        register_package_for_domain("test", "test-package")
        
        packages = get_packages_for_domain("test")
        
        assert "test-package" in packages
    
    def test_register_package_creates_domain_if_missing(self):
        """Test that registering package auto-creates domain."""
        register_package_for_domain("autodomain", "pkg1")
        
        assert "autodomain" in _domain_interfaces
        packages = get_packages_for_domain("autodomain")
        assert "pkg1" in packages
    
    def test_get_packages_for_domain_returns_empty_set(self):
        """Test getting packages for unregistered domain."""
        packages = get_packages_for_domain("nonexistent")
        assert packages == set()
    
    def test_register_multiple_packages_for_domain(self):
        """Test registering multiple packages for same domain."""
        register_domain_interface("test", {"name": "test"})
        register_package_for_domain("test", "pkg1")
        register_package_for_domain("test", "pkg2")
        register_package_for_domain("test", "pkg3")
        
        packages = get_packages_for_domain("test")
        
        assert len(packages) == 3
        assert "pkg1" in packages
        assert "pkg2" in packages


class TestSchemaRegistration:
    """Tests for domain schema registration."""
    
    def setup_method(self):
        """Clear registries before each test."""
        _domain_interfaces.clear()
        _domain_packages.clear()
    
    def test_register_domain_schema(self):
        """Test registering a schema for a domain."""
        schema = {"type": "object", "properties": {}}
        
        register_domain_schema("test", "TestSchema", schema)
        
        interface = get_domain_interface("test")
        assert "schemas" in interface
        assert len(interface["schemas"]) == 1
        assert interface["schemas"][0]["name"] == "TestSchema"
    
    def test_register_schema_creates_domain_if_missing(self):
        """Test that schema registration auto-creates domain."""
        schema = {"type": "string"}
        
        register_domain_schema("newdomain", "Schema1", schema)
        
        assert "newdomain" in _domain_interfaces
    
    def test_register_multiple_schemas(self):
        """Test registering multiple schemas for domain."""
        schema1 = {"type": "string"}
        schema2 = {"type": "number"}
        
        register_domain_schema("test", "Schema1", schema1)
        register_domain_schema("test", "Schema2", schema2)
        
        interface = get_domain_interface("test")
        assert len(interface["schemas"]) == 2
    
    def test_register_schema_updates_existing(self):
        """Test that re-registering schema updates it."""
        old_schema = {"type": "string"}
        new_schema = {"type": "number"}
        
        register_domain_schema("test", "Schema1", old_schema)
        register_domain_schema("test", "Schema1", new_schema)
        
        interface = get_domain_interface("test")
        assert len(interface["schemas"]) == 1
        assert interface["schemas"][0]["schema"] == new_schema


class TestFunctionRegistration:
    """Tests for domain function registration."""
    
    def setup_method(self):
        """Clear registries before each test."""
        _domain_interfaces.clear()
        _domain_packages.clear()
    
    def test_register_domain_function(self):
        """Test registering a function for domain."""
        def test_func():
            return "test"
        
        register_domain_function("test", "test_func", test_func)
        
        interface = get_domain_interface("test")
        assert "functions" in interface
        assert len(interface["functions"]) == 1
        assert interface["functions"][0]["name"] == "test_func"
    
    def test_get_domain_function(self):
        """Test retrieving registered function."""
        def test_func():
            return 42
        
        register_domain_function("test", "test_func", test_func)
        result = get_domain_function("test", "test_func")
        
        assert result == test_func
        assert result() == 42
    
    def test_get_domain_function_returns_none_for_missing(self):
        """Test getting non-existent function returns None."""
        result = get_domain_function("test", "nonexistent")
        assert result is None
    
    def test_register_multiple_functions(self):
        """Test registering multiple functions."""
        def func1():
            return 1
        def func2():
            return 2
        
        register_domain_function("test", "func1", func1)
        register_domain_function("test", "func2", func2)
        
        interface = get_domain_interface("test")
        assert len(interface["functions"]) == 2
    
    def test_register_function_updates_existing(self):
        """Test that re-registering function updates it."""
        def old_func():
            return "old"
        def new_func():
            return "new"
        
        register_domain_function("test", "func", old_func)
        register_domain_function("test", "func", new_func)
        
        interface = get_domain_interface("test")
        assert len(interface["functions"]) == 1
        
        result = get_domain_function("test", "func")
        assert result() == "new"
