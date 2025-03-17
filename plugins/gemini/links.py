"""Gemini LLM link type implementation."""
from typing import Dict, Any, List, Optional
import json
import os
import logging
import google.generativeai as genai
from jinja2 import Environment, BaseLoader, StrictUndefined

from core.links import LinkHandler, register_link_type

# Simple JSON extraction functionality
def extract_json(text: str) -> str:
    """Extract valid JSON from text using simple extraction."""
    import re
    import json
    
    # Try direct parsing first
    try:
        json.loads(text)
        return text
    except:
        pass
    
    # Try to extract from code blocks
    code_block_pattern = r"\`\`\`json(.*?)\`\`\`"
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        try:
            json.loads(match.group(1))
            return match.group(1)
        except:
            pass
    
    # Try to extract from any JSON-like structure
    json_pattern = r"\{.*?\}"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            json.loads(match.group(0))
            return match.group(0)
        except:
            pass
    
    return ""

class GeminiLinkHandler(LinkHandler):
    """Handler for Gemini LLM link type."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "default-model")
        self.environment = Environment(loader=BaseLoader(), undefined=StrictUndefined)
    
    def handle_link(self, link: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle the link and return the processed result."""
        prompt = self.environment.from_string(link).render(context or {})
        response = genai.generate(prompt, api_key=self.api_key, model=self.model)
        return extract_json(response)

register_link_type("gemini", GeminiLinkHandler)