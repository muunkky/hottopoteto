INSERT_SCHEMA = {
    "type": "object",
    "required": ["collection", "document"],
    "properties": {
        "collection": {"type": "string"},
        "document": {"type": "object"}
    }
}

FIND_SCHEMA = {
    "type": "object",
    "required": ["collection"],
    "properties": {
        "collection": {"type": "string"},
        "filter": {"type": "object"},
        "projection": {"type": "object"},
        "sort": {"type": "object"}
    }
}
