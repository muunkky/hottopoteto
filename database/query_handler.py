# database/query_handler.py
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
