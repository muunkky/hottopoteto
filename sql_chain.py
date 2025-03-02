from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools import QuerySQLDatabaseTool

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

# Example usage
step_config = {"db_uri": "sqlite:///Chinook.db"}
query_chain = build_sql_chain(step_config)

# Example: Generate a SQL query from natural language input
query = query_chain.invoke({"question": "How many employees are there?"})
print("Generated Query:", query)

# Execute the query
execute_query = QuerySQLDatabaseTool(db=SQLDatabase.from_uri(step_config["db_uri"]))
result = execute_query.invoke(query)
print("Query Result:", result)
