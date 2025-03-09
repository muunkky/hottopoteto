# database/db_connection.py
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def get_db_connection(db_settings: dict) -> Engine:
    """
    Create and return a SQLAlchemy Engine based on the provided database settings.
    
    Args:
        db_settings (dict): Database configuration parameters.
    
    Returns:
        Engine: A SQLAlchemy engine instance.
    """
    connection_string = db_settings.get("connection_string")
    if not connection_string:
        # Build connection string from individual settings if needed
        user = db_settings.get("user")
        password = db_settings.get("password")
        host = db_settings.get("host")
        database = db_settings.get("database")
        connection_string = f"postgresql://{user}:{password}@{host}/{database}"
    engine = create_engine(connection_string)
    return engine

def execute_query(engine, query: str, params: dict = None):
    """
    Execute a SQL query using the provided SQLAlchemy engine.
    
    Args:
        engine: SQLAlchemy Engine instance.
        query (str): SQL query string to execute.
        params (dict, optional): Query parameters.
    
    Returns:
        list: Fetched results from the query.
    """
    with engine.connect() as connection:
        result = connection.execute(query, params or {})
        return result.fetchall()
