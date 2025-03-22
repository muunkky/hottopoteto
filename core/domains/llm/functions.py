"""
Functions for LLM domain
"""
from typing import Dict, Any, Optional
from core.registration import register_domain_function  # Import the registration function

def generate_text(prompt: str, model: str = "gpt-4o", temperature: float = 0.7, 
                  provider: str = "openai", system: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate text using a language model.
    
    Args:
        prompt: The prompt to generate text from
        model: The model to use
        temperature: The sampling temperature
        provider: The provider to use
        system: Optional system prompt
        
    Returns:
        A dictionary containing the generated text
    """
    # Example implementation (replace with actual API call)
    system_context = f"[System: {system}] " if system else ""
    
    # In a real implementation, we would call the LLM API here
    # For now, we'll just mock a response
    sample_responses = [
        "Hello! Welcome to Hottopoteto! I'm here to help you with your tasks.",
        "Welcome! I'm excited to assist you with Hottopoteto today.",
        "Greetings! It's great to have you using Hottopoteto.",
        "Hi there! Welcome to the Hottopoteto system. How can I help you today?"
    ]
    
    import random
    response_text = random.choice(sample_responses)
    
    return {
        "text": response_text,
        "model": model,
        "temperature": temperature,
        "provider": provider
    }

def list_available_models(provider: str = "openai") -> Dict[str, Any]:
    """
    List available models from a provider
    
    Args:
        provider: The provider to query
        
    Returns:
        Dictionary containing available models
    """
    # Mock implementation
    models_by_provider = {
        "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "gemini": ["gemini-pro", "gemini-ultra"]
    }
    
    return {
        "models": models_by_provider.get(provider, []),
        "provider": provider
    }

def complete_prompt(prompt: str, model: str = "gpt-4o", provider: str = "openai") -> Dict[str, Any]:
    """
    Complete a prompt using a language model
    
    Args:
        prompt: The prompt to complete
        model: The model to use
        provider: The provider to use
        
    Returns:
        Completion result
    """
    return generate_text(prompt, model, 0.0, provider)

# Register domain functions so they're available to the function registry
register_domain_function("llm", "generate_text", generate_text)
register_domain_function("llm", "list_available_models", list_available_models)
register_domain_function("llm", "complete_prompt", complete_prompt)
