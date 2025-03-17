"""MongoDB link type implementation."""
from typing import Dict, Any
from pymongo import MongoClient

from core.links import LinkHandler, register_link_type

class MongoDBLinkHandler(LinkHandler):
    """Handler for mongodb link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a MongoDB operation."""
        operation = link_config.get("operation", "find")
        uri = link_config.get("uri", "mongodb://localhost:27017")
        database = link_config.get("database")
        collection = link_config.get("collection")
        
        # Connect to MongoDB
        client = MongoClient(uri)
        db = client[database]
        coll = db[collection]
        
        # Process operation inputs
        inputs = {}
        for key, value_template in link_config.get("inputs", {}).items():
            # Process template to replace variables with values from context
            # This would use a template engine like Jinja2
            inputs[key] = cls._process_template(value_template, context)
        
        # Execute operation
        result = None
        if operation == "insert":
            result = {"inserted_id": str(coll.insert_one(inputs).inserted_id)}
        elif operation == "find":
            cursor = coll.find(inputs)
            result = {"documents": list(cursor)}
        elif operation == "update":
            filter_query = inputs.get("filter", {})
            update_dict = inputs.get("update", {})
            result = {"modified_count": coll.update_many(filter_query, update_dict).modified_count}
        elif operation == "delete":
            result = {"deleted_count": coll.delete_many(inputs).deleted_count}
            
        return result
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the schema for MongoDB link configuration."""
        return {
            "type": "object",
            "required": ["operation", "database", "collection"],
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["insert", "find", "update", "delete"],
                    "description": "MongoDB operation to perform"
                },
                "uri": {
                    "type": "string",
                    "description": "MongoDB connection URI"
                },
                "database": {
                    "type": "string",
                    "description": "MongoDB database name"
                },
                "collection": {
                    "type": "string",
                    "description": "MongoDB collection name"
                },
                "inputs": {
                    "type": "object",
                    "description": "Operation-specific parameters"
                }
            }
        }
    
    @classmethod
    def _process_template(cls, template, context):
        """Process a template string with values from context."""
        # Simplified implementation - would use a proper template engine
        if isinstance(template, str) and "{{" in template and "}}" in template:
            for key, value in context.items():
                template = template.replace(f"{{{{ {key} }}}}", str(value))
        return template

# Register the MongoDB link type
register_link_type("mongodb", MongoDBLinkHandler)
