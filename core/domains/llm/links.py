"""
Link handlers for the LLM domain
"""
from typing import Dict, Any
import logging
from core.links import LinkHandler, register_link_type
from .functions import generate_text

logger = logging.getLogger(__name__)

class LLMHandler(LinkHandler):
    """Handler for LLM link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the LLM link."""
        model = link_config.get("model", "gpt-4o")
        prompt = link_config.get("prompt", "")
        temperature = link_config.get("temperature", 0.7)
        provider = link_config.get("provider", "openai")
        system = link_config.get("system", "You are a helpful assistant.")
        output_schema = link_config.get("output_schema")
        
        # Generate text using the LLM function
        result = generate_text(prompt, model=model, temperature=temperature, provider=provider, system=system)
        
        # Extract structured data if schema is provided
        if output_schema and "properties" in output_schema:
            # For our simple example with a greeting property
            if "greeting" in output_schema.get("properties", {}):
                return {
                    "raw": result["text"],
                    "data": {
                        "greeting": result["text"]
                    }
                }
        
        # Default case - return the raw text
        return {
            "raw": result["text"],
            "data": {
                "raw_content": result["text"]
            }
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for this link type's configuration."""
        return {
            "type": "object",
            "required": ["prompt"],
            "properties": {
                "model": {"type": "string", "description": "LLM model to use"},
                "prompt": {"type": "string", "description": "Prompt to generate text"},
                "system": {"type": "string", "description": "System prompt"},
                "temperature": {"type": "number", "description": "Sampling temperature"},
                "provider": {"type": "string", "description": "LLM provider"},
                "output_schema": {
                    "type": "object",
                    "description": "Schema for structured output"
                }
            }
        }

# Register the link type
register_link_type("llm", LLMHandler)
