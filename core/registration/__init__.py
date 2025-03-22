"""
Registration functions for the core system.
"""
# Export domain registration functions
from .domains import (
    register_domain_interface,
    register_package_for_domain,
    get_packages_for_domain,
    get_domain_interface,
    list_domains,
    register_domain_schema,
    register_domain_function,
    get_domain_function
)
