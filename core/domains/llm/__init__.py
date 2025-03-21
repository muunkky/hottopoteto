"""
LLM domain implementation
"""
from core.registry import PackageRegistry
from core.registration import register_domain_interface
from core.security.credentials import register_domain_credentials

# Register domain with the system
register_domain_interface("llm", {
    "name": "llm",
    "version": "0.1.0",
    "description": "Language Model operations for text generation and completion"
})

# Register this domain as being provided by the core package
PackageRegistry.register_domain_from_package(
    "core",  # The package providing this domain
    "llm",  # The domain name
    __name__  # This module
)

# Register required credentials for this domain
register_domain_credentials("llm", [
    {
        "name": "OPENAI_API_KEY",
        "description": "OpenAI API key for GPT models",
        "required": True
    },
    {
        "name": "ANTHROPIC_API_KEY",
        "description": "Anthropic API key for Claude models",
        "required": False
    },
    {
        "name": "GEMINI_API_KEY",
        "description": "Google Gemini API key",
        "required": False
    }
])

# Don't import providers module here - it creates a circular dependency
# Import individual components instead
from .models import LLMMessage, LLMRequest, LLMResponse, LLMProvider
from .functions import generate_text, list_available_models

# The links module will be imported by the core links discovery system
