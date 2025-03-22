"""
Conlang plugin for constructed language creation
"""
import os
from core.registry import PackageRegistry
from core.templates import register_template_directory

# Plugin root directory
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))

# Register this plugin
def register():
    """Register the conlang plugin"""
    PackageRegistry.register_plugin_from_package(
        "core",  # Package name (using core since it's built-in)
        "conlang",  # Plugin name
        __name__  # Module reference
    )
    
    # Register plugin template directories if they exist
    text_templates_dir = os.path.join(PLUGIN_DIR, "templates", "text")
    if os.path.exists(text_templates_dir):
        register_template_directory("text", text_templates_dir)
        
    recipe_templates_dir = os.path.join(PLUGIN_DIR, "templates", "recipes")
    if os.path.exists(recipe_templates_dir):
        register_template_directory("recipes", recipe_templates_dir)
    
    # Import components to trigger their registration
    from . import links
    from . import processors
    
    # Import domain implementations
    from .domains import linguistics
