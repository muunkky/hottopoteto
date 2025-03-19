"""
Linguistics domain implementation provided by the conlang plugin
"""
from core.registry import PackageRegistry
# Import from our new registration module
from core.registration import register_domain_interface

# Register domain with the system
register_domain_interface("linguistics", {
    "name": "linguistics",
    "version": "0.1.0",
    "description": "Language and linguistic analysis tools"
})

# Register this domain as being provided by the conlang plugin
# This indicates that the conlang plugin "owns" this domain
PackageRegistry.register_domain_from_package(
    "conlang",  # The plugin providing this domain
    "linguistics",  # The domain name
    __name__  # This module
)

# Import domain components
from . import models
from . import functions
