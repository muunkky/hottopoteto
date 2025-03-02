# chains/sql_chain.py
from langchain_community.chains.sql_database.base import SQLDatabaseChain
from database.db_connection import get_db_connection
from utils.config_loader import load_config

def build_sql_chain(step_config: dict) -> SQLDatabaseChain:
    """
    Build a SQLDatabaseChain for a 'sql' step.
    
    Args:
        step_config (dict): Dictionary containing the step configuration from YAML.
    
    Returns:
        SQLDatabaseChain: A configured SQL database chain.
    """
    # Load SQL query from file if specified
    if "query" in step_config:
        with open(step_config["query"], "r") as file:
            sql_query = file.read()
    else:
        sql_query = ""
    
    # Load the database configuration
    db_config_path = step_config.get("db_config", "configs/db_config.yaml")
    db_settings = load_config(db_config_path)
    
    # Get a SQLAlchemy engine based on the database settings
    db = get_db_connection(db_settings)
    
    # Build and return the SQLDatabaseChain
    sql_chain = SQLDatabaseChain.from_llm(
        llm=None,  # Optionally, provide an LLM if query interpretation is required
        database=db,
        query=sql_query
    )
    return sql_chain
