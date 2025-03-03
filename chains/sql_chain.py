# chains/sql_chain.py
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools import QuerySQLDatabaseTool
from database.db_connection import get_db_connection
from utils.config_loader import load_config
import os
import yaml
from config import DATABASE_URL  # Centralized configuration

def build_sql_chain(step_config: dict):
    """
    Build a chain that converts a question to a SQL query and executes it.
    
    Args:
        step_config (dict): The configuration for this SQL step.
    
    Returns:
        A SQL query chain that generates and executes SQL queries.
    """
    # Use the SQLite database
    DB_URI = os.getenv("DATABASE_URL", "sqlite:///database/data.db")

    # Connect to SQLite
    db = SQLDatabase.from_uri(DB_URI)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Create the SQL query generator chain
    query_chain = create_sql_query_chain(llm, db)
    
    return query_chain

def execute_sql_step(step_config, context):
    # Use DATABASE_URL from the centralized config (DB must be initialized via init_db.py/schema.sql)
    from config import DATABASE_URL
    import logging
    
    db = SQLDatabase.from_uri(DATABASE_URL)
    
    # Load query text (either from a .sql file or inline)
    if step_config["query"].endswith(".sql"):
        with open(step_config["query"], "r") as file:
            query_text = file.read()
        logging.info(f"Loaded SQL from file: {step_config['query']}")
    else:
        query_text = step_config["query"]
        logging.info(f"Using inline SQL: {query_text}")
    
    # Create a params dictionary specifically for query substitution
    sql_params = {}
    for param_name, param_value in step_config.get("parameters", {}).items():
        # If it's a placeholder, get the actual value from context
        if isinstance(param_value, str) and param_value.startswith("{{") and param_value.endswith("}}"):
            placeholder = param_value.strip("{}")
            if placeholder in context:
                sql_params[param_name] = context[placeholder]
            else:
                # Try to handle dotted notation (e.g. Step1_output.category)
                parts = placeholder.split(".")
                if parts[0] in context and len(parts) > 1:
                    obj = context[parts[0]]
                    for part in parts[1:]:
                        if isinstance(obj, dict) and part in obj:
                            obj = obj[part]
                        # For other types, just use the value if available
                    sql_params[param_name] = obj
        else:
            sql_params[param_name] = param_value
    
    logging.info(f"SQL Parameters after processing: {sql_params}")
    
    # Format query with parameters
    try:
        query = query_text.format(**sql_params)
        logging.info(f"Formatted SQL query: {query}")
    except KeyError as e:
        logging.error(f"Parameter substitution error: {e}")
        return {"error": f"Parameter substitution error: {e}"}
    
    # Execute the query with graceful error handling
    try:
        # For debugging, let's verify the records table content
        check_query = "SELECT * FROM records"
        result = db.run(check_query)
        logging.info(f"Records table content: {result}")
        
        # Now run the actual query
        result = db.run(query)
        logging.info(f"SQL result: {result}")
        return result
    except Exception as e:
        logging.error(f"SQL execution error: {e}")
        # Return an error string or dict to allow graceful handling downstream
        return {"error": f"SQL execution error: {str(e)}"}
