# core/registry.py
class FunctionRegistry:
    """
    Registry for functions callable from recipes.
    
    This registry allows functions to be registered by name and then later
    called by that name from within recipes using the function link type.
    """
    
    _functions = {}
    
    @classmethod
    def register(cls, name, func, meta=None):
        """
        Register a function.
        
        Args:
            name: Unique name for the function
            func: The function to register
            meta: Optional metadata about the function
        """
        cls._functions[name] = {
            'function': func,
            'metadata': meta or {}
        }
    
    @classmethod
    def get(cls, name):
        """
        Get a registered function.
        
        Args:
            name: Name of the function to retrieve
            
        Returns:
            Function object or None if not found
        """
        return cls._functions.get(name, {}).get('function')

class PackageRegistry:
    """
    Central registry for packages, domains, and plugins.
    
    This registry tracks all loaded packages and their provided components,
    such as domains and plugins. It maintains the relationships between 
    these components for lookup and discovery.
    """
    _packages = {}
    _domains = {}
    _plugins = {}
    _core_package = None
    
    @classmethod
    def register_core_package(cls, package_module):
        """
        Register the core package itself.
        
        Core packages have special status and provide foundational functionality.
        
        Args:
            package_module: The module object for the core package
        """
        cls._core_package = package_module
        # Register as a special package
        cls._packages['core'] = {
            'module': package_module,
            'type': 'core',
            'version': getattr(package_module, '__version__', '0.1.0')
        }
        
    @classmethod
    def register_package(cls, name, package_module):
        """
        Register a package and its resources.
        
        Extension packages provide additional functionality beyond the core.
        
        Args:
            name: Name of the package
            package_module: The module object for the package
        """
        cls._packages[name] = {
            'module': package_module,
            'type': 'extension',
            'version': getattr(package_module, '__version__', '0.1.0')
        }
        
    @classmethod
    def is_core_package(cls, name):
        """
        Check if a package is the core package.
        
        Args:
            name: Name of the package to check
            
        Returns:
            True if it's a core package, False otherwise
        """
        return name == 'core' or (
            name in cls._packages and 
            cls._packages[name].get('type') == 'core'
        )
    
    @classmethod
    def get_package_type(cls, name):
        """
        Get the type of a package (core or extension).
        
        Args:
            name: Name of the package
            
        Returns:
            'core', 'extension', or None if package not found
        """
        if name not in cls._packages:
            return None
        return cls._packages[name].get('type', 'extension')
    
    @classmethod
    def get_package(cls, name):
        """
        Get a registered package by name.
        
        Args:
            name: Name of the package
            
        Returns:
            Package info dictionary or None if not found
        """
        return cls._packages.get(name)
    
    @classmethod
    def list_packages(cls):
        """
        List all registered packages.
        
        Returns:
            List of package names
        """
        return list(cls._packages.keys())
        
    @classmethod
    def register_domain_from_package(cls, package_name, domain_name, domain_module):
        """
        Register a domain provided by a package.
        
        This creates the association between a package and a domain it implements.
        
        Args:
            package_name: Name of the package providing the domain
            domain_name: Name of the domain
            domain_module: The module object for the domain
            
        Raises:
            ValueError: If the package is not registered
        """
        if package_name not in cls._packages:
            raise ValueError(f"Package {package_name} is not registered")
            
        if domain_name not in cls._domains:
            cls._domains[domain_name] = []
            
        cls._domains[domain_name].append({
            "package": package_name,
            "module": domain_module
        })
        
        # Register with domains system - import at runtime to avoid circular imports
        import importlib
        try:
            # Try to import from registration first (preferred)
            registration = importlib.import_module('core.registration')
            registration.register_package_for_domain(domain_name, package_name)
        except (ImportError, AttributeError):
            # Fall back to core.domains
            try:
                domains = importlib.import_module('core.domains')
                domains.register_package_for_domain(domain_name, package_name)
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to register package for domain: {e}")
        
    @classmethod
    def register_plugin_from_package(cls, package_name, plugin_name, plugin_module):
        """
        Register a plugin provided by a package.
        
        This creates the association between a package and a plugin it provides.
        
        Args:
            package_name: Name of the package providing the plugin
            plugin_name: Name of the plugin
            plugin_module: The module object for the plugin
            
        Raises:
            ValueError: If the package is not registered
        """
        if package_name not in cls._packages:
            raise ValueError(f"Package {package_name} is not registered")
            
        if plugin_name not in cls._plugins:
            cls._plugins[plugin_name] = []
            
        cls._plugins[plugin_name].append({
            "package": package_name,
            "module": plugin_module
        })