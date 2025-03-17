GENERATION_PARAMS_SCHEMA = {
    "type": "object",
    "properties": {
        "model": {
            "type": "string",
            "enum": ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
        },
        "temperature": {"type": "number", "minimum": 0, "maximum": 1},
        "top_p": {"type": "number", "minimum": 0, "maximum": 1},
        "top_k": {"type": "integer", "minimum": 1},
        "max_tokens": {"type": "integer", "minimum": 1}
    }
}
