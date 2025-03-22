"""
Hottopoteto - A flexible framework for building AI-powered applications
"""
import os
import sys
import logging
import pkg_resources

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Register the core package first
try:
    from core.registry import PackageRegistry
    # Register the core package itself
    PackageRegistry.register_core_package(sys.modules[__name__])
    logger.info("Core package registered successfully")
except Exception as e:
    logger.error(f"Failed to register core package: {e}")

def discover_packages():
    """Discover and initialize installed packages"""
    packages_found = []
    
    try:
        for entry_point in pkg_resources.iter_entry_points("hottopoteto.packages"):
            try:
                package_name = entry_point.name
                register_func = entry_point.load()
                register_func()
                packages_found.append(package_name)
                logger.info(f"Loaded package: {package_name}")
            except Exception as e:
                logger.error(f"Failed to load package '{entry_point.name}': {e}")
    except Exception as e:
        logger.error(f"Error during package discovery: {e}")
        
    return packages_found

# Initialize packages on import
discovered_packages = discover_packages()
logger.info(f"Discovered {len(discovered_packages)} packages: {', '.join(discovered_packages) if discovered_packages else 'none'}")
