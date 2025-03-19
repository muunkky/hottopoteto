"""
Storage domain implementation
"""
from core.registry import PackageRegistry
from core.registration import register_domain_interface

# Register domain interface
register_domain_interface("storage", {
    "name": "storage",
    "version": "0.1.0",
    "description": "Data storage and retrieval operations"
})

# Register this domain as being provided by the core package
PackageRegistry.register_domain_from_package(
    "core",  # The package providing this domain
    "storage",  # The domain name
    __name__  # This module
)

# Import components AFTER registration
# This avoids circular imports
# These components will be loaded by the discovery system
