# Domain Organization Guidelines

Each domain should organize code following these guidelines:

## models.py - Data Structures

Models should contain:
- **Data models** (Pydantic models, schemas)
- **Class definitions** with minimal behavior
- **Type definitions**
- **Data validation** logic
- **Schema registration**

Example:
```python
class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    
    def validate_email(self) -> bool:
        # Simple validation is OK
        return "@" in self.email
        
register_domain_schema("users", "profile", UserProfile.schema())
```

## functions.py - Domain Logic

Functions should contain:
- **Business logic** operations
- **Processing functions**
- **Domain-specific behaviors**
- **Function registration**

Example:
```python
def create_user(name: str, email: str) -> Dict[str, Any]:
    """Create a new user"""
    user_id = generate_id()
    user = UserProfile(id=user_id, name=name, email=email)
    
    if not user.validate_email():
        return {"success": False, "error": "Invalid email"}
    
    result = storage.save("users", user.dict())
    return {"success": True, "user_id": user_id}
    
register_domain_function("users", "create_user", create_user)
```

## utils.py - Shared Utilities

Utilities should contain:
- **Helper functions** not tied to domain concepts
- **I/O operations** (file, network, DB access)
- **Generic utilities** shared across the domain

Example:
```python
def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())
    
def ensure_directory(path: str) -> bool:
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
    return os.path.exists(path)
```

## Avoiding Circular Imports

1. **Bottom-up dependency**: Utils → Models → Functions → Links
2. **Models** should not import from Functions
3. **Functions** can import from Models and Utils
4. **Utils** should be self-contained without domain imports

When you need a utility in both models and functions, put it in utils.py.
