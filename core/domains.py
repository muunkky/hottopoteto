"""Domain interface registry and utilities."""
# Simple re-export from registration module
from core.registration.domains import (
    register_domain_interface,
    register_package_for_domain,
    get_packages_for_domain,
    get_domain_interface,
    list_domains,
    register_domain_schema,
    register_domain_function,
    get_domain_function
)

# Export all symbols from the registration module
__all__ = [
    'register_domain_interface',
    'register_package_for_domain',
    'get_packages_for_domain',
    'get_domain_interface',
    'list_domains',
    'register_domain_schema',
    'register_domain_function',
    'get_domain_function'
]
