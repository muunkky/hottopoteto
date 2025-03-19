"""
Utilities for creating package templates
"""
import os
import shutil
from core.utils import ensure_directory

TEMPLATES = {
    "setup.py": """
from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    description="A Hottopoteto package",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    entry_points={{
        "hottopoteto.packages": [
            "{module_name}=hottopoteto_{module_name}:register",
        ],
    }},
    install_requires=["hottopoteto"],
)
""",
    "__init__.py": """
def register():
    from core.registry import PackageRegistry
    
    # Register the package
    PackageRegistry.register_package("{module_name}", __name__)
    
    # Import and register package components
    from . import components
"""
}

DOMAIN_TEMPLATE = {
    "domains/__init__.py": """
# Import domain modules here
from . import {domain_name}
""",
    "domains/{domain_name}/__init__.py": """
from core.registry import PackageRegistry
from core.domains import register_domain_interface

# Register domain with the system
register_domain_interface("{domain_name}", {{
    "name": "{domain_name}",
    "version": "0.1.0",
    "description": "A domain for {domain_name}"
}})

# Register this domain with the package
PackageRegistry.register_domain_from_package(
    "{module_name}", 
    "{domain_name}", 
    __name__
)
""",
    "domains/{domain_name}/models.py": """
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from core.models import GenericEntryModel

class {domain_name_cap}Entry(GenericEntryModel):
    \"\"\"Base model for {domain_name} entries\"\"\"
    name: str
    description: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
"""
}

PLUGIN_TEMPLATE = {
    "plugins/__init__.py": """
# Import plugin modules here
from . import {plugin_name}
""",
    "plugins/{plugin_name}/__init__.py": """
from core.registry import PackageRegistry

# Register plugin with the package
PackageRegistry.register_plugin_from_package(
    "{module_name}",
    "{plugin_name}",
    __name__
)

# Import plugin components
from . import links
""",
    "plugins/{plugin_name}/links.py": """
from typing import Dict, Any
from core.links import LinkHandler, register_link_type

class {plugin_name_cap}LinkHandler(LinkHandler):
    \"\"\"Handler for {plugin_name} links\"\"\"
    
    @classmethod
    def execute(cls, link_config, context):
        # Implement link execution
        return {"result": "success"}
    
    @classmethod
    def get_schema(cls):
        return {{
            "type": "object",
            "properties": {{
                "param1": {{"type": "string", "description": "A parameter"}}
            }}
        }}

# Register the link type
register_link_type("{plugin_name}", {plugin_name_cap}LinkHandler)
"""
}

def create_package_template(package_name, module_name, options=None):
    """Create a package template directory structure"""
    if options is None:
        options = {}
        
    # Create base directory
    base_dir = os.path.join(os.getcwd(), package_name)
    ensure_directory(base_dir)
    
    # Create module directory
    module_dir = os.path.join(base_dir, f"hottopoteto_{module_name}")
    ensure_directory(module_dir)
    
    # Create base files
    for filename, template in TEMPLATES.items():
        with open(os.path.join(module_dir, filename), "w") as f:
            f.write(template.format(
                package_name=package_name,
                module_name=module_name
            ).strip())
    
    # Create components module
    components_dir = os.path.join(module_dir, "components")
    ensure_directory(components_dir)
    with open(os.path.join(components_dir, "__init__.py"), "w") as f:
        f.write("# Register components here")
    
    # Add domain template if requested
    if "domain" in options and options["domain"]:
        domain_name = options["domain"]
        domains_dir = os.path.join(module_dir, "domains")
        ensure_directory(domains_dir)
        domain_dir = os.path.join(domains_dir, domain_name)
        ensure_directory(domain_dir)
        
        for filename, template in DOMAIN_TEMPLATE.items():
            filepath = os.path.join(module_dir, filename.format(domain_name=domain_name))
            ensure_directory(os.path.dirname(filepath))
            
            with open(filepath, "w") as f:
                f.write(template.format(
                    domain_name=domain_name,
                    domain_name_cap=domain_name.capitalize(),
                    module_name=module_name
                ).strip())
    
    # Add plugin template if requested
    if "plugin" in options and options["plugin"]:
        plugin_name = options["plugin"]
        plugins_dir = os.path.join(module_dir, "plugins")
        ensure_directory(plugins_dir)
        plugin_dir = os.path.join(plugins_dir, plugin_name)
        ensure_directory(plugin_dir)
        
        for filename, template in PLUGIN_TEMPLATE.items():
            filepath = os.path.join(module_dir, filename.format(plugin_name=plugin_name))
            ensure_directory(os.path.dirname(filepath))
            
            with open(filepath, "w") as f:
                f.write(template.format(
                    plugin_name=plugin_name,
                    plugin_name_cap=plugin_name.capitalize(),
                    module_name=module_name
                ).strip())
    
    # Create a README.md
    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write(f"""# {package_name}

A package for Hottopoteto.

## Installation

```bash
pip install -e .
```

## Features

- Add your features here
""")

    return base_dir
