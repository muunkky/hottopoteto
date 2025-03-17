CREATE_TABLE_SCHEMA = {
    "type": "object",
    "required": ["table_name", "columns"],
    "properties": {
        "table_name": {"type": "string"},
        "columns": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "constraints": {"type": "string"}
                }
            }
        }
    }
}
