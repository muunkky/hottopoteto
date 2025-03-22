import os
import unittest
from unittest.runner import TextTestRunner
from unittest.suite import TestSuite
from pathlib import Path
import pytest
import logging
import inspect

# Add project root to path if needed
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in os.sys.path:
    os.sys.path.insert(0, str(project_root))

# Import domain registration functions for checking registered domains
from core.registration.domains import list_domains


# Documentation references for helpful error messages
DOCS = {
    # Plugin documentation
    "plugin_structure": "docs/guides/creating_plugins.md",
    
    # Domain documentation
    "domain_structure": "docs/guides/creating-domains.md#domain-structure",
    
    # General architecture 
    "architecture": "docs/concepts/architecture.md",
    
    # Architecture principles
    "principles": "docs/reference/architecture-principles-summary.md",
    
    # Package documentation
    "package_structure": "docs/guides/creating-packages.md",
    
    # ADRs for more detailed explanations
    "domain_isolation": "docs/architecture/decisions/adr-0001-domain-isolation-pattern.md",
    "domain_registration": "docs/architecture/decisions/adr-0002-domain-registration-system.md",
    "plugin_discovery": "docs/architecture/decisions/adr-0003-plugin-discovery-mechanism.md"
}

def get_doc_link(doc_key):
    """Generate a helpful documentation link for error messages."""
    if doc_key in DOCS:
        relative_path = DOCS[doc_key]
        # For command line, show the relative path
        # For IDE test runners that support links, provide the full path
        full_path = os.path.join(str(project_root), relative_path)
        return f"See: {relative_path} (full path: {full_path})"
    return ""


@pytest.mark.architecture
class TestDirectoryStructure(unittest.TestCase):
    """Tests that verify domains and plugins follow the required directory structure."""
    
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
        cls.logger.info("Starting Directory Structure Tests")
        
        # Define paths to main directories
        cls.project_root = project_root
        cls.core_dir = cls.project_root / 'core'
        cls.domains_dir = cls.core_dir / 'domains'
        cls.plugins_dir = cls.project_root / 'plugins'
        
        # Import main to trigger domain registrations
        import main
        
        # Track test statistics
        cls.stats = {
            "core_files_checked": 0,
            "core_directories_checked": 0,
            "domains_checked": 0,
            "plugins_checked": 0,
            "warnings": 0
        }
    
    def test_core_directory_structure(self):
        """Test that the core directory has the required structure."""
        # Core directory should exist
        self.assertTrue(self.core_dir.exists(), "Core directory does not exist")
        self.assertTrue(self.core_dir.is_dir(), "Core path is not a directory")
        
        # Core should have an __init__.py file
        init_file = self.core_dir / '__init__.py'
        self.assertTrue(
            init_file.exists(), 
            f"Core directory has no __init__.py file. {get_doc_link('architecture')}"
        )
        
        # Check for required core subdirectories
        required_dirs = ['domains', 'links', 'registration']
        for dir_name in required_dirs:
            dir_path = self.core_dir / dir_name
            self.assertTrue(
                dir_path.exists() and dir_path.is_dir(), 
                f"Required core subdirectory '{dir_name}' missing. {get_doc_link('architecture')}"
            )
            
            # Each subdirectory should have an __init__.py
            subdir_init = dir_path / '__init__.py'
            self.assertTrue(
                subdir_init.exists(), 
                f"Core subdirectory '{dir_name}' has no __init__.py file. {get_doc_link('architecture')}"
            )
            self.__class__.stats["core_directories_checked"] += 1
        
        # Check for required core files
        required_files = ['executor.py', 'schemas.py']
        for file_name in required_files:
            file_path = self.core_dir / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Required core file '{file_name}' missing. {get_doc_link('architecture')}"
            )
            self.__class__.stats["core_files_checked"] += 1
            
        self.logger.info(f"✓ Core structure validated with {self.__class__.stats['core_directories_checked']} directories and {self.__class__.stats['core_files_checked']} files")
    
    def test_domains_directory_structure(self):
        """Test that each domain follows the required directory structure."""
        # Domains directory should exist
        self.assertTrue(
            self.domains_dir.exists(), 
            f"Domains directory does not exist. {get_doc_link('domain_structure')}"
        )
        self.assertTrue(
            self.domains_dir.is_dir(), 
            f"Domains path is not a directory. {get_doc_link('domain_structure')}"
        )
        
        # Get all registered domains
        registered_domains = list_domains()
        self.logger.info(f"Testing structure of {len(registered_domains)} registered domains")
        
        # Check each registered domain against expected structure
        for domain_name in registered_domains:
            # Skip testing core domains that might not have explicit directories
            if domain_name in ('core', 'base', 'system'):
                continue
                
            domain_dir = self.domains_dir / domain_name
            
            # The domain should have a directory
            self.assertTrue(
                domain_dir.exists() and domain_dir.is_dir(),
                f"Domain '{domain_name}' is registered but has no directory. {get_doc_link('domain_structure')}"
            )
            
            # Each domain directory should have an __init__.py file
            init_file = domain_dir / '__init__.py'
            self.assertTrue(
                init_file.exists(),
                f"Domain '{domain_name}' directory has no __init__.py file. {get_doc_link('domain_structure')}"
            )
            
            # Test for common expected subdirectories (if this is your pattern)
            expected_files = [
                '__init__.py',
                'links.py',  # Links implementation
            ]
            
            # Check for expected files (keeping the validation soft)
            for file_name in expected_files:
                file_path = domain_dir / file_name
                if not file_path.exists():
                    self.logger.warning(
                        f"Domain '{domain_name}' is missing expected file: {file_name}"
                    )
                    self.__class__.stats["warnings"] += 1
                    
            self.__class__.stats["domains_checked"] += 1
            
        self.logger.info(f"✓ Validated structure of {self.__class__.stats['domains_checked']} domains")
    
    def test_plugins_directory_structure(self):
        """Test that the plugins directory follows the required structure."""
        # Check if plugins directory exists
        if not self.plugins_dir.exists():
            self.logger.info("Plugins directory does not exist yet - skipping test")
            return
        
        self.assertTrue(
            self.plugins_dir.is_dir(), 
            f"Plugins path is not a directory. {get_doc_link('plugin_structure')}"
        )
        
        # Enumerate plugin directories
        plugin_dirs = [
            item for item in self.plugins_dir.iterdir() 
            if item.is_dir() and not item.name.startswith('__')
        ]
        
        if not plugin_dirs:
            self.logger.info("No plugins found - skipping detailed structure check")
            return
            
        self.logger.info(f"Testing structure of {len(plugin_dirs)} plugins")
        
        # Check each plugin's structure
        for plugin_dir in plugin_dirs:
            plugin_name = plugin_dir.name
            
            # Each plugin directory should have an __init__.py file
            init_file = plugin_dir / '__init__.py'
            self.assertTrue(
                init_file.exists(),
                f"Plugin '{plugin_name}' directory has no __init__.py file.\n{get_doc_link('plugin_structure')}"
            )
            
            # Each plugin should have a plugin.yaml or plugin.json config
            has_config = (plugin_dir / 'plugin.yaml').exists() or (plugin_dir / 'plugin.json').exists()
            self.assertTrue(
                has_config,
                f"Plugin '{plugin_name}' has no plugin.yaml or plugin.json configuration file.\n"
                f"{get_doc_link('plugin_structure')}\n"
                f"See ADR: {get_doc_link('plugin_discovery')}\n"
                f"Required: Create either '{plugin_name}/plugin.yaml' or '{plugin_name}/plugin.json'"
            )
            
            self.__class__.stats["plugins_checked"] += 1
            
        self.logger.info(f"✓ Validated structure of {self.__class__.stats['plugins_checked']} plugins")
    
    def test_domain_directory_contents(self):
        """Validate that domain directories contain expected implementation files."""
        # This test provides a more detailed check of domain contents
        
        # First get all domain directories in the domains folder
        domain_dirs = [
            item for item in self.domains_dir.iterdir() 
            if item.is_dir() and not item.name.startswith('__')
        ]
        
        domains_with_links = 0
        domains_with_api = 0
        domains_with_interface = 0
        domains_with_models = 0
        domains_with_schemas = 0
        
        for domain_dir in domain_dirs:
            domain_name = domain_dir.name
            
            # Look for at least one of these implementation patterns
            has_links = (domain_dir / 'links.py').exists()
            has_api = (domain_dir / 'api.py').exists() 
            has_interface = (domain_dir / 'interface.py').exists()
            has_models = (domain_dir / 'models.py').exists()
            
            if has_links: domains_with_links += 1
            if has_api: domains_with_api += 1
            if has_interface: domains_with_interface += 1
            if has_models: domains_with_models += 1
            
            # Domain should implement at least one of these patterns
            self.assertTrue(
                has_links or has_api or has_interface or has_models,
                f"Domain '{domain_name}' is missing expected implementation files.\n"
                f"{get_doc_link('domain_structure')}\n"
                f"Required: At least one of: links.py, api.py, interface.py, models.py"
            )
            
            # Check if domain has a schema directory or schema definitions
            has_schemas = (domain_dir / 'schemas').is_dir() or (domain_dir / 'schemas.py').exists()
            if has_schemas: domains_with_schemas += 1
            
            # This is more of an informational check
            if not has_schemas:
                self.logger.warning(f"Domain '{domain_name}' has no schema definitions")
                self.__class__.stats["warnings"] += 1
                
        self.logger.info(f"✓ Domain implementation patterns: links: {domains_with_links}, api: {domains_with_api}, interface: {domains_with_interface}, models: {domains_with_models}, schemas: {domains_with_schemas}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        cls.logger.info(f"Directory Structure Tests completed with {cls.stats['warnings']} warnings")


if __name__ == '__main__':
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # Configure color output if colorama is available
    try:
        from colorama import init, Fore, Style
        init()
        has_colors = True
    except ImportError:
        has_colors = False
    
    # Add summary information
    def run_tests():
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDirectoryStructure)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        
        # Print summary
        print("\n" + "="*60)
        if has_colors:
            print(f"{Fore.GREEN}Directory Structure Test Summary:{Style.RESET_ALL}")
        else:
            print("Directory Structure Test Summary:")
            
        print(f"✓ {result.testsRun} architecture patterns verified")
        
        # Get test class instance to access stats
        test_instance = TestDirectoryStructure()
        stats = TestDirectoryStructure.stats
        
        print(f"✓ Core structure: {stats['core_directories_checked']} directories, {stats['core_files_checked']} files")
        print(f"✓ Domains structure: {stats['domains_checked']} domains checked")
        print(f"✓ Plugins structure: {stats['plugins_checked']} plugins checked")
        
        if stats["warnings"] > 0:
            warning_text = f"{stats['warnings']} warnings"
            if has_colors:
                print(f"{Fore.YELLOW}⚠ {warning_text}{Style.RESET_ALL}")
            else:
                print(f"⚠ {warning_text}")
                
        # Detailed structure display
        if has_colors:
            print(f"\n{Fore.CYAN}Component Structure Details:{Style.RESET_ALL}")
        else:
            print("\nComponent Structure Details:")
        print("-" * 60)
        
        # Show domain structure table
        domains_dir = test_instance.domains_dir
        if domains_dir.exists():
            domain_dirs = [
                item for item in domains_dir.iterdir() 
                if item.is_dir() and not item.name.startswith('__')
            ]
            
            if domain_dirs:
                print(f"{'Domain':<20} {'Links':<8} {'API':<8} {'Interface':<10} {'Models':<8} {'Schemas':<8}")
                print("-" * 60)
                
                for domain_dir in sorted(domain_dirs):
                    domain_name = domain_dir.name
                    has_links = "✓" if (domain_dir / 'links.py').exists() else "-"
                    has_api = "✓" if (domain_dir / 'api.py').exists() else "-"
                    has_interface = "✓" if (domain_dir / 'interface.py').exists() else "-"
                    has_models = "✓" if (domain_dir / 'models.py').exists() else "-"
                    has_schemas = "✓" if ((domain_dir / 'schemas').is_dir() or 
                                          (domain_dir / 'schemas.py').exists()) else "-"
                    
                    print(f"{domain_name:<20} {has_links:<8} {has_api:<8} {has_interface:<10} {has_models:<8} {has_schemas:<8}")
        
        # Show plugin structure table
        plugins_dir = test_instance.plugins_dir
        if plugins_dir.exists():
            plugin_dirs = [
                item for item in plugins_dir.iterdir() 
                if item.is_dir() and not item.name.startswith('__')
            ]
            
            if plugin_dirs:
                print("\n")
                print(f"{'Plugin':<20} {'Init':<8} {'Config':<8}")
                print("-" * 40)
                
                for plugin_dir in sorted(plugin_dirs):
                    plugin_name = plugin_dir.name
                    has_init = "✓" if (plugin_dir / '__init__.py').exists() else "-"
                    has_config = "✓" if ((plugin_dir / 'plugin.yaml').exists() or 
                                         (plugin_dir / 'plugin.json').exists()) else "-"
                    
                    print(f"{plugin_name:<20} {has_init:<8} {has_config:<8}")
        
        print("="*60)
        
        return result
    
    result = run_tests()
    sys.exit(not result.wasSuccessful())