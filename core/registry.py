# core/registry.py
class FunctionRegistry:
    """Registry for functions callable from recipes."""
    
    _functions = {}
    
    @classmethod
    def register(cls, name, func, meta=None):
        """Register a function."""
        cls._functions[name] = {
            'function': func,
            'metadata': meta or {}
        }
    
    @classmethod
    def get(cls, name):
        """Get a registered function."""
        return cls._functions.get(name, {}).get('function')