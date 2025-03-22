"""
Core package for Hottopoteto
"""
import logging

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Register the core package
from core.registry import PackageRegistry
PackageRegistry.register_core_package(__name__)
logger.info("Core package registered")

# DO NOT import core components here - it creates circular imports!
# Import these modules in the specific files that need them instead
