"""SQLite link type implementation."""
from typing import Dict, Any, List
import sqlite3
import os
from core.links import LinkHandler, register_link_type

class SQLiteHandler(LinkHandler):
    """Handler for sqlite link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a SQLite operation."""
        operation = link_config.get("operation", "query")
        db_path = link_config.get("database", "recipe_data.db")
        
        # Process inputs with template substitution
        inputs = {}
        for key, value_template in link_config.get("inputs", {}).items():
            inputs[key] = cls._process_template(value_template, context)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        result = {}
        
        try:
            if operation == "create_table":
                table_name = inputs.get("table_name")
                columns = inputs.get("columns", [])
                if not table_name or not columns:
                    raise ValueError("Table name and columns required for create_table")
                    
                column_defs = ", ".join([f"{col['name']} {col['type']}" for col in columns])
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
                cursor.execute(sql)
                result = {"table_created": table_name}
                
            elif operation == "insert":
                table_name = inputs.get("table_name")
                data = inputs.get("data", {})
                if not table_name or not data:
                    raise ValueError("Table name and data required for insert")
                    
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data.keys()])
                values = list(data.values())
                
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                result = {"inserted_id": cursor.lastrowid}
                
            elif operation == "query":
                sql = inputs.get("sql")
                params = inputs.get("params", [])
                if not sql:
                    raise ValueError("SQL required for query")
                    
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                result = {"rows": [dict(row) for row in rows]}
                
            elif operation == "update":
                sql = inputs.get("sql")
                params = inputs.get("params", [])
                if not sql:
                    raise ValueError("SQL required for update")
                    
                cursor.execute(sql, params)
                result = {"modified_count": cursor.rowcount}
                
            elif operation == "delete":
                table_name = inputs.get("table_name")
                condition = inputs.get("condition", "1=1")
                params = inputs.get("params", [])
                
                sql = f"DELETE FROM {table_name} WHERE {condition}"
                cursor.execute(sql, params)
                result = {"deleted_count": cursor.rowcount}
            
            # Commit changes
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            result = {"error": str(e)}
            
        finally:
            conn.close()
            
        return result
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type."""
        return {
            "type": "object",
            "required": ["operation", "database"],
            "properties": {
                "operation": {
                    "type": "string", 
                    "enum": ["create_table", "insert", "query", "update", "delete"],
                    "description": "SQLite operation to perform"
                },
                "database": {
                    "type": "string",
                    "description": "Path to SQLite database file"
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
        if isinstance(template, str) and "{{" in template and "}}" in template:
            for key, value in context.items():
                if key in context and isinstance(context[key], dict) and "data" in context[key]:
                    # Handle nested data references
                    for subkey, subvalue in context[key]["data"].items():
                        template = template.replace(
                            f"{{{{ {key}.data.{subkey} }}}}", 
                            str(subvalue)
                        )
                template = template.replace(f"{{{{ {key} }}}}", str(value))
        return template

# Register the SQLite link type
register_link_type("sqlite", SQLiteHandler)
