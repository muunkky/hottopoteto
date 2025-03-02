# chains/sql_chain.py
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools import QuerySQLDatabaseTool
from database.db_connection import get_db_connection
from utils.config_loader import load_config

def build_sql_chain(step_config: dict):
    """
    Build a chain that converts a question to a SQL query and executes it.
    
    Args:
        step_config (dict): The configuration for this SQL step.
    
    Returns:
        A SQL query chain that generates and executes SQL queries.
    """
    db = SQLDatabase.from_uri(step_config["db_uri"])  # Example: "sqlite:///Chinook.db"
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Create the SQL query generator chain
    query_chain = create_sql_query_chain(llm, db)
    
    return query_chain
