import unittest
from unittest.runner import TextTestRunner
from unittest.suite import TestSuite
import importlib
import inspect
import os
import sys
import logging
from pathlib import Path
import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.registration.domains import (
    list_domains,
    get_domain_interface,
    get_packages_for_domain,
    register_domain_interface,
    register_package_for_domain,
    register_domain_schema,
    register_domain_function
)


# Add pytest marker for architecture tests
@pytest.mark.architecture
class TestDomainRegistrationPattern(unittest.TestCase):
    """Tests to verify that domains follow the correct registration pattern."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        cls.logger = logging.getLogger('architecture.tests')
        
        # Announce start of architecture tests
        cls.logger.info("Starting Domain Registration Architecture Tests")
        
        # Import the main module to trigger all registrations
        import main
        
        # Log detected domains
        cls.logger.info(f"Detected {len(list_domains())} registered domains: {', '.join(list_domains())}")
    
    def setUp(self):
        """Ensure the test environment is properly set up."""
        # Store original domains state for later checks
        self.initial_domains = set(list_domains())
        
    def test_domain_interfaces_have_required_fields(self):
        """Verify that all domain interfaces have the required fields."""
        domains_checked = 0
        
        for domain_name in list_domains():
            interface = get_domain_interface(domain_name)
            
            self.assertIsNotNone(interface, f"Domain {domain_name} has no interface")
            self.assertIn("name", interface, f"Domain {domain_name} interface missing 'name' field")
            self.assertIn("version", interface, f"Domain {domain_name} interface missing 'version' field")
            
            # Either schemas or functions should be present
            has_schemas = "schemas" in interface and isinstance(interface["schemas"], list)
            has_functions = "functions" in interface and isinstance(interface["functions"], list)
            
            self.assertTrue(
                has_schemas or has_functions,
                f"Domain {domain_name} interface has neither schemas nor functions"
            )
            domains_checked += 1
            
        self.logger.info(f"✓ Verified {domains_checked} domains have required interface fields")
            
    def test_domain_schemas_properly_structured(self):
        """Verify that domain schemas follow the expected structure."""
        for domain_name in list_domains():
            interface = get_domain_interface(domain_name)
            
            if "schemas" in interface and interface["schemas"]:
                for schema in interface["schemas"]:
                    self.assertIn("name", schema, f"Schema in domain {domain_name} missing 'name'")
                    self.assertTrue(
                        "schema" in schema or "data" in schema,
                        f"Schema {schema.get('name', 'unknown')} in domain {domain_name} has no schema data"
                    )
                    
    def test_domain_functions_properly_registered(self):
        """Verify that domain functions are properly registered."""
        for domain_name in list_domains():
            interface = get_domain_interface(domain_name)
            
            if "functions" in interface and interface["functions"]:
                for function in interface["functions"]:
                    self.assertIn("name", function, 
                                f"Function in domain {domain_name} missing 'name'")
                    self.assertTrue(
                        "function" in function or "data" in function,
                        f"Function {function.get('name', 'unknown')} in domain {domain_name} has no implementation"
                    )
    
    def test_domain_directory_structure(self):
        """Verify that domains registered have corresponding directory structures."""
        base_path = Path(__file__).parent.parent.parent / 'core' / 'domains'
        
        for domain_name in list_domains():
            # Skip testing core domains that might not have explicit directories
            if domain_name in ('core', 'base', 'system'):
                continue
                
            domain_dir = base_path / domain_name
            self.assertTrue(
                domain_dir.exists() and domain_dir.is_dir(),
                f"Domain {domain_name} is registered but has no directory at {domain_dir}"
            )
            
            # Check for __init__.py
            init_file = domain_dir / '__init__.py'
            self.assertTrue(
                init_file.exists() and init_file.is_file(),
                f"Domain {domain_name} directory exists but has no __init__.py file"
            )
    
    def test_packages_properly_associated_with_domains(self):
        """Verify that packages are properly associated with domains."""
        # This test may need to be adjusted based on how packages are defined in your system
        for domain_name in list_domains():
            packages = get_packages_for_domain(domain_name)
            
            # Simply ensure the return is a set for now
            self.assertIsInstance(packages, set, 
                                f"Packages for domain {domain_name} should be a set")
            
            # If we know specific domains should have packages, we can test them
            # For example:
            if domain_name == "llm":
                self.assertTrue(len(packages) > 0, 
                              f"Domain {domain_name} should have at least one package")
                
    def test_domain_registration_idempotence(self):
        """Verify that registering a domain twice doesn't cause issues."""
        # Register a test domain
        test_domain = "test_domain_registration"
        register_domain_interface(test_domain, {
            "name": test_domain,
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        })
        
        # Try registering it again with the same data
        register_domain_interface(test_domain, {
            "name": test_domain,
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        })
        
        # Verify it's still registered properly
        self.assertIn(test_domain, list_domains())
        interface = get_domain_interface(test_domain)
        self.assertEqual(interface["name"], test_domain)
        self.assertEqual(interface["version"], "1.0.0")
        
    def test_domain_schemas_registration(self):
        """Verify that schemas can be properly registered to domains."""
        # Register a test domain
        test_domain = "test_schema_registration"
        register_domain_interface(test_domain, {
            "name": test_domain,
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        })
        
        # Register a schema
        test_schema = {
            "type": "object",
            "properties": {
                "test": {"type": "string"}
            }
        }
        register_domain_schema(test_domain, "test_schema", test_schema)
        
        # Verify schema is registered
        interface = get_domain_interface(test_domain)
        schemas = interface.get("schemas", [])
        
        schema_found = False
        for schema in schemas:
            if schema.get("name") == "test_schema":
                schema_found = True
                schema_data = schema.get("schema", {})
                self.assertEqual(schema_data["type"], "object")
                break
                
        self.assertTrue(schema_found, f"Schema 'test_schema' not found in domain {test_domain}")
        
    def test_domain_functions_registration(self):
        """Verify that functions can be properly registered to domains."""
        # Register a test domain
        test_domain = "test_function_registration"
        register_domain_interface(test_domain, {
            "name": test_domain,
            "version": "1.0.0",
            "schemas": [],
            "functions": []
        })
        
        # Define a test function
        def test_function(input_data):
            return {"result": input_data}
            
        # Register the function
        register_domain_function(test_domain, "test_function", test_function)
        
        # Verify function is registered
        from core.registration.domains import get_domain_function
        function = get_domain_function(test_domain, "test_function")
        
        self.assertIsNotNone(function, f"Function 'test_function' not found in domain {test_domain}")
        self.assertEqual(function({"test": "value"}), {"result": {"test": "value"}})
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        cls.logger.info("All Domain Registration Architecture Tests completed")


if __name__ == '__main__':
    # Create a custom test runner
    runner = TextTestRunner(verbosity=2)  # Increased verbosity
    
    # Configure color output if colorama is available
    try:
        from colorama import init, Fore, Style
        init()
        has_colors = True
    except ImportError:
        has_colors = False
    
    # Add summary information
    def run_tests():
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDomainRegistrationPattern)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "="*60)
        if has_colors:
            print(f"{Fore.GREEN}Architecture Test Summary:{Style.RESET_ALL}")
        else:
            print("Architecture Test Summary:")
            
        print(f"✓ {result.testsRun} domain registration patterns verified")
        
        domains = list_domains()
        print(f"✓ {len(domains)} domains checked")
        
        # Detailed domain information
        domains_with_schemas = 0
        domains_with_functions = 0
        total_schemas = 0
        total_functions = 0
        
        print("\nDomain Details:")
        print("-" * 40)
        print(f"{'Domain':<20} {'Version':<10} {'Schemas':<10} {'Functions':<10}")
        print("-" * 40)
        
        for domain in sorted(domains):
            interface = get_domain_interface(domain)
            version = interface.get("version", "N/A")
            schemas = interface.get("schemas", [])
            functions = interface.get("functions", [])
            
            if schemas:
                domains_with_schemas += 1
                total_schemas += len(schemas)
            
            if functions:
                domains_with_functions += 1
                total_functions += len(functions)
                
            print(f"{domain:<20} {version:<10} {len(schemas):<10} {len(functions):<10}")
        
        print("-" * 40)
        print(f"✓ {domains_with_schemas} domains with schemas ({total_schemas} total schemas)")
        print(f"✓ {domains_with_functions} domains with functions ({total_functions} total functions)")
        print("="*60)
        
        return result
    
    result = run_tests()
    sys.exit(not result.wasSuccessful())