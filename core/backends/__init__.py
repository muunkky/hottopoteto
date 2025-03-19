"""
Backwards compatibility module for storage backends.
This has been replaced by the domain models approach but is kept for compatibility.

DEPRECATED: Use core.domains.storage.models instead.
"""
import logging
import warnings
from typing import Dict, Any, Type, Optional, List, TypeVar, Generic

logger = logging.getLogger(__name__)

warnings.warn(
    "The core.backends module is deprecated. Use core.domains.storage.models instead.",
    DeprecationWarning,
    stacklevel=2
)

# Type for backend implementations
T = TypeVar('T')

class BackendRegistry(Generic[T]):
    """Generic registry for domain backends. (DEPRECATED)"""
    
    def __init__(self, backend_type: str):
        self._backend_type = backend_type
        self._backends = {}
        
    def register(self, name: str, backend: T) -> None:
        """Register a backend implementation."""
        self._backends[name] = backend
        logger.info(f"Registered {self._backend_type} backend: {name}")
        
    def get(self, name: str) -> Optional[T]:
        """Get a registered backend by name."""
        if name not in self._backends:
            logger.warning(f"{self._backend_type} backend '{name}' not found")
            return None
        return self._backends[name]
        
    def list(self) -> List[str]:
        """List all registered backends."""
        return list(self._backends.keys())

class BackendService:
    """Base class for domain backend services. (DEPRECATED)"""
    
    @classmethod
    def initialize(cls, config: Dict[str, Any]) -> 'BackendService':
        """Initialize a backend instance with configuration."""
        raise NotImplementedError("Backend services must implement initialize")
