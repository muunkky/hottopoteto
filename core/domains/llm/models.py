"""
Model definitions for LLM domain
"""
from typing import Dict, List, Any, Optional, ClassVar, Type
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from core.security.credentials import get_credential

# Data models
class LLMMessage(BaseModel):
    """A message in an LLM conversation"""
    role: str
    content: str

class LLMRequest(BaseModel):
    """Request to an LLM provider"""
    messages: List[LLMMessage] = Field(default_factory=list)
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the request"""
        self.messages.append(LLMMessage(role=role, content=content))

class LLMResponse(BaseModel):
    """Response from an LLM provider"""
    content: str
    model: str
    provider: str

# Service models
class LLMProvider(BaseModel):
    """Base model for LLM providers"""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    
    # Use class variable for registry
    _registry: ClassVar[Dict[str, Type['LLMProvider']]] = {}
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text with this provider"""
        raise NotImplementedError("LLM providers must implement generate method")
    
    @classmethod
    def register(cls, provider_class: Type['LLMProvider']) -> None:
        """Register a provider implementation"""
        # Use a class property from the model as the registry key
        cls._registry[provider_class.__fields__["name"].default] = provider_class
        
    @classmethod
    def get(cls, name: str) -> Optional[Type['LLMProvider']]:
        """Get a provider by name"""
        return cls._registry.get(name)
        
    @classmethod
    def list(cls) -> List[str]:
        """List all registered providers"""
        return list(cls._registry.keys())

# Provider implementations
class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation"""
    name: str = "openai"
    base_url: str = "https://api.openai.com/v1"
    models: List[str] = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI"""
        # Get API key from environment variables
        api_key = get_credential("OPENAI_API_KEY")
        
        # In a real implementation, this would call the OpenAI API
        # For now, we'll just mock a response
        import random
        sample_responses = [
            "Hello! I'm here to help you with your tasks.",
            "Welcome! I'm excited to assist you today.",
            "Greetings! How can I help you?"
        ]
        
        return LLMResponse(
            content=random.choice(sample_responses),
            model=request.model,
            provider=self.name
        )

# Register provider implementations
LLMProvider.register(OpenAIProvider)

# Register schemas with domain schema registry
from core.registration import register_domain_schema

register_domain_schema("llm", "message", {
    "type": "object",
    "required": ["role", "content"],
    "properties": {
        "role": {"type": "string", "description": "Role of the message sender"},
        "content": {"type": "string", "description": "Content of the message"}
    }
})

register_domain_schema("llm", "request", {
    "type": "object",
    "required": ["messages", "model"],
    "properties": {
        "messages": {
            "type": "array",
            "items": {"$ref": "#/definitions/llm.message"},
            "description": "Messages in the conversation"
        },
        "model": {"type": "string", "description": "LLM model to use"},
        "temperature": {"type": "number", "description": "Sampling temperature"},
        "provider": {"type": "string", "description": "LLM provider"}
    }
})

register_domain_schema("llm", "response", {
    "type": "object",
    "required": ["content", "model", "provider"],
    "properties": {
        "content": {"type": "string", "description": "Generated content"},
        "model": {"type": "string", "description": "Model used for generation"},
        "provider": {"type": "string", "description": "Provider used for generation"}
    }
})
