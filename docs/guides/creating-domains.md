# Creating Domains in Hottopoteto

This guide explains how to create custom domains in Hottopoteto.

## What is a Domain?

In Hottopoteto, a domain represents a specialized knowledge area with its own:

- Data models (schemas)
- Processing functions
- CLI commands
- Utilities specific to that knowledge area

Examples of domains include constructed languages (conlang), storytelling, LLM interactions, and data processing.

## Domain Structure

Every domain must follow this standard directory structure:

```
domains/domain_name/            # Domain root directory
├── __init__.py                 # Registration code
├── models.py                   # Data models and schemas
├── functions.py                # Domain-specific functions
├── utils.py                    # Utilities specific to this domain
├── links/                      # Domain-specific link handlers
│   └── __init__.py
├── cli/                        # CLI commands for this domain
│   └── __init__.py
├── schemas/                    # JSON schemas
│   └── __init__.py
└── README.md                   # Domain documentation
```

## Step-by-Step Guide

### 1. Create the Domain Directory

First, create a directory for your domain:

```bash
mkdir -p hottopoteto/domains/my_domain
cd hottopoteto/domains/my_domain
```

### 2. Register the Domain

Create an `__init__.py` file that registers the domain with the system:

```python
from core.registry import PackageRegistry
from core.domains import register_domain_interface

# Register domain interface
register_domain_interface("my_domain", {
    "name": "my_domain",
    "version": "1.0.0",
    "description": "Description of my custom domain"
})

# Register with package (if part of a package)
# If this is part of the core, you can use:
PackageRegistry.register_domain_from_package(
    "core", 
    "my_domain", 
    __name__
)
```

### 3. Define Domain Models

Create a `models.py` file with your domain's data models:

```python
from pydantic import BaseModel, Field
from core.domains import register_domain_schema
from typing import List, Optional

class MyEntity(BaseModel):
    """Entity model for my domain."""
    id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic config."""
        schema_extra = {
            "examples": [{
                "id": "entity-001",
                "name": "Example Entity",
                "description": "This is an example entity",
                "tags": ["example", "demo"]
            }]
        }

# Register schema
register_domain_schema("my_domain", "entity", MyEntity.schema())
```

### 4. Implement Domain Functions

Create a `functions.py` file with your domain-specific logic:

```python
from typing import Dict, Any, List
from core.domains import register_domain_function
from .models import MyEntity

def create_entity(name: str, description: str = None, tags: List[str] = None) -> Dict[str, Any]:
    """Create a new entity in this domain.
    
    Args:
        name: Entity name
        description: Optional entity description
        tags: Optional list of tags
        
    Returns:
        Dictionary with entity data
    """
    import uuid
    
    # Generate a unique ID
    entity_id = f"entity-{str(uuid.uuid4())[:8]}"
    
    # Create entity
    entity = MyEntity(
        id=entity_id,
        name=name,
        description=description,
        tags=tags or []
    )
    
    # Return as dictionary
    return entity.dict()

# Register function
register_domain_function("my_domain", "create_entity", create_entity)
```

### 5. Add Domain Utilities

Create a `utils.py` file for helper functions:

```python
def is_valid_entity_id(entity_id: str) -> bool:
    """Check if an entity ID is valid for this domain.
    
    Args:
        entity_id: Entity ID to check
        
    Returns:
        True if valid, False otherwise
    """
    return entity_id.startswith("entity-") and len(entity_id) >= 10
```

### 6. Implement Domain-Specific Links

Create a links directory for custom link types:

```bash
mkdir -p links
touch links/__init__.py
```

Add a link handler in `links/__init__.py`:

```python
from typing import Dict, Any, ClassVar
from core.links import LinkHandler, register_link_type

class MyDomainLinkHandler(LinkHandler):
    """Handler for my_domain.operation link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the my_domain.operation link.
        
        Args:
            link_config: Link configuration
            context: Execution context
            
        Returns:
            Link output
        """
        # Get parameters
        name = link_config.get("name", "Unnamed")
        description = link_config.get("description", None)
        
        # Import domain function
        from ..functions import create_entity
        
        # Call domain function
        result = create_entity(name=name, description=description)
        
        # Return result
        return {"data": result}
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the schema for this link type.
        
        Returns:
            Link configuration schema
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Entity name"
                },
                "description": {
                    "type": "string",
                    "description": "Entity description"
                }
            },
            "required": ["name"]
        }

# Register the link type
register_link_type("my_domain.create", MyDomainLinkHandler)
```

### 7. Add CLI Commands

Create a cli directory for custom commands:

```bash
mkdir -p cli
touch cli/__init__.py
```

Add CLI commands in `cli/__init__.py`:

```python
import click
from core.cli import cli_group

@cli_group.group("my_domain")
def my_domain_cli():
    """My domain CLI commands."""
    pass

@my_domain_cli.command("create")
@click.option("--name", "-n", required=True, help="Entity name")
@click.option("--description", "-d", help="Entity description")
def create_entity_command(name, description):
    """Create a new entity in my domain."""
    from ..functions import create_entity
    
    result = create_entity(name=name, description=description)
    click.echo(f"Created entity: {result['id']}")
    click.echo(f"Name: {result['name']}")
    if result.get("description"):
        click.echo(f"Description: {result['description']}")
```

### 8. Document Your Domain

Create a README.md file to document your domain:

```markdown
# My Domain

This domain provides functionality for managing custom entities.

## Features

- Create and manage entities
- Custom link types for recipes
- CLI commands for entity management

## Usage in Recipes

```yaml
name: "Example Recipe"
links:
  - name: "Create_Entity"
    type: "my_domain.create"
    name: "My Entity"
    description: "A custom entity created from a recipe"
```

## CLI Commands

```bash
# Create an entity
python main.py my_domain create --name "My Entity" --description "A custom entity"
```
```

## Testing Your Domain

### 1. Create a Test Recipe

Create a recipe that uses your domain:

```yaml
name: "Test My Domain"
description: "Testing my custom domain"
version: "1.0"
links:
  - name: "Create_Entity"
    type: "my_domain.create"
    name: "Test Entity"
    description: "Entity created by test recipe"
    
  - name: "Display_Entity"
    type: "log"
    level: "info"
    message: "Created entity: {{ Create_Entity.data.id }} - {{ Create_Entity.data.name }}"
```

### 2. Run Your Recipe

```bash
python main.py execute --recipe_file recipes/test_my_domain.yaml
```

### 3. Test CLI Commands

```bash
python main.py my_domain create --name "CLI Entity" --description "Entity created via CLI"
```

## Packaging Your Domain

To distribute your domain as a package, use the package creation tool:

```bash
python main.py packages create my_package --domain my_domain
```

This will create a package template that you can customize and distribute. See the [Creating Packages](creating-packages.md) guide for more details.

## Best Practices

1. **Follow Standard Structure**: Adhere to the standard domain directory structure
2. **Register Everything**: Register all models, functions, and link types
3. **Document Domain Features**: Add clear documentation for your domain
4. **Add Examples**: Include example recipes that use your domain
5. **Version Your Domain**: Include version information in your domain interface
6. **Use Domain Prefixes**: Prefix link types with your domain name
7. **Include Validation**: Validate inputs to your domain functions
8. **Error Handling**: Use clear error messages for domain-specific errors
9. **Follow Naming Conventions**: Use snake_case for all identifiers
