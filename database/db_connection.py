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
