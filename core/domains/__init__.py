"""
Core domains package.

This package contains domain implementations that are part of the core system.
Each subdirectory represents a specific domain with its own models, functions, and utilities.
"""
# Do NOT import from core.domains here as it creates a circular import!

# Instead, simply define this as a package
# Domains are automatically loaded when their respective modules are imported
# This happens through the registry system when the domains register themselves
