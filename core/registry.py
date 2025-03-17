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

class PackageRegistry:
    _packages = {}
    _domains = {}
    _plugins = {}
    _core_package = None
    
    @classmethod
    def register_core_package(cls, package_module):
        """Register the core package itself"""
        cls._core_package = package_module
        # Register as a special package
        cls._packages['core'] = {
            'module': package_module,
            'type': 'core',
            'version': getattr(package_module, '__version__', '0.1.0')
        }
        
    @classmethod
    def register_package(cls, name, package_module):
        """Register a package and its resources"""
        cls._packages[name] = {
            'module': package_module,
            'type': 'extension',
            'version': getattr(package_module, '__version__', '0.1.0')
        }
        
    @classmethod
    def is_core_package(cls, name):
        """Check if a package is the core package"""
        return name == 'core' or (
            name in cls._packages and 
            cls._packages[name].get('type') == 'core'
        )
    
    @classmethod
    def get_package_type(cls, name):
        """Get the type of a package (core or extension)"""
        if name not in cls._packages:
            return None
        return cls._packages[name].get('type', 'extension')
    
    @classmethod
    def get_package(cls, name):
        """Get a registered package by name"""
        return cls._packages.get(name)
    
    @classmethod
    def list_packages(cls):
        """List all registered packages"""
        return list(cls._packages.keys())
        
    @classmethod
    def register_domain_from_package(cls, package_name, domain_name, domain_module):
        """Register a domain provided by a package"""
        if package_name not in cls._packages:
            raise ValueError(f"Package {package_name} is not registered")
            
        if domain_name not in cls._domains:
            cls._domains[domain_name] = []
            
        cls._domains[domain_name].append({
            "package": package_name,
            "module": domain_module
        })
        
        # Register with domains system
        from core.domains import register_package_for_domain
        register_package_for_domain(domain_name, package_name)
        
    @classmethod
    def register_plugin_from_package(cls, package_name, plugin_name, plugin_module):
        """Register a plugin provided by a package"""
        if package_name not in cls._packages:
            raise ValueError(f"Package {package_name} is not registered")
            
        if plugin_name not in cls._plugins:
            cls._plugins[plugin_name] = []
            
        cls._plugins[plugin_name].append({
            "package": package_name,
            "module": plugin_module
        })