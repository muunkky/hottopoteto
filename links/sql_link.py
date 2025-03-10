import logging
import os
import sqlite3
from typing import Dict, Any, List, Optional, ClassVar
from pydantic import BaseModel, Field, field_validator
from langchain_community.utilities import SQLDatabase
from config import DATABASE_URL
from links.base_link import BaseLink, LinkConfig, OutputData, LinkOutput

class SQLLinkConfig(LinkConfig):
    """Extended configuration for SQL link with specific fields"""
    DEFAULT_TYPE: ClassVar[str] = "sql"
    DEFAULT_DATABASE_URL: ClassVar[str] = DATABASE_URL
    
    # Required fields
    query: str
    
    # Optional fields with defaults from class constants
    database_url: str = Field(default_factory=lambda: SQLLinkConfig.DEFAULT_DATABASE_URL)
    
    @field_validator('type', mode='before')
    @classmethod
    def set_default_type(cls, v):
        return v or cls.DEFAULT_TYPE
    
    @field_validator('database_url', mode='before')
    @classmethod
    def set_default_database(cls, v):
        return v or cls.DEFAULT_DATABASE_URL

class SQLLink(BaseLink):
    """Link for executing SQL queries."""
    
    def __init__(self):
        self.connection = None

    def _connect(self, database_url: str):
        # Handle SQLite URL: "sqlite:///path/to/db.sqlite"
        if (database_url.startswith("sqlite:///")):
            file_path = database_url.replace("sqlite:///", "", 1)
            file_path = os.path.abspath(file_path)
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            logging.debug(f"Connecting to SQLite database at: {file_path}")
            self.connection = sqlite3.connect(file_path)
        else:
            logging.debug(f"Connecting to external DB: {database_url}")
            self.connection = sqlite3.connect(database_url)
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        """
        Validate SQL link configuration.
        
        Args:
            config: The LinkConfig object to validate
        
        Raises:
            ValueError: If validation fails
        """
        if not config.query:
            raise ValueError("SQL step requires a 'query' field")
            
        if isinstance(config.query, str) and config.query.endswith(".sql"):
            try:
                self._validate_file_path(config.query)
            except ValueError as e:
                raise ValueError(f"SQL file validation error: {str(e)}")
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        """
        Execute SQL query based on configuration.
        
        Args:
            config: The SQLLinkConfig object
            context: Current execution context
        
        Returns:
            Query results in a dictionary format
        
        Raises:
            ValueError: If query fails
        """
    
        step_name = config.name
        logger = logging.getLogger(__name__)  # Make sure we have logger defined
        logger.trace(f"Executing SQL step: {step_name}")
        
        query = config.query
        database_url = config.database_url or SQLLinkConfig.DEFAULT_DATABASE_URL
        
        if not query:
            raise ValueError("Query not found in configuration")
        
        try:
            if not self.connection:
                self._connect(database_url)
            
            # Get the query text from file or inline
            if query.endswith(".sql"):
                query_text = self.read_template_file(query)
            else:
                query_text = query
                
            query_preview = query_text[:100] + ("..." if len(query_text) > 100 else "")
            logger.trace(f"Using SQL: {query_preview}")
            
            # Generic placeholder extraction and parameterization
            import re
            placeholders = re.findall(r"{{([^{}]+)}}", query_text)
            param_values = []
            
            # Create parameterized query by replacing {{...}} with ?
            parameterized_query = query_text
            for placeholder in placeholders:
                full_placeholder = f"{{{{{placeholder}}}}}"
                # Resolve the actual value
                value = self.resolve_placeholders_in_text(full_placeholder, context)
                param_values.append(value)
                # Replace with parameter placeholder
                parameterized_query = parameterized_query.replace(full_placeholder, "?")
            
            logger.trace(f"Parameterized query: {parameterized_query}")
            logger.trace(f"Parameter values: {param_values}")
            
            cursor = self.connection.cursor()
            cursor.execute(parameterized_query, param_values)
            
            # Process results
            result = []
            column_names = []
            if cursor.description:  # This will be None for non-SELECT queries
                rows = cursor.fetchall()
                column_names = [col[0] for col in cursor.description]
                
                # Convert to list of dictionaries for better usability
                for row in rows:
                    result.append(dict(zip(column_names, row)))
                    
            # For INSERT/UPDATE/DELETE, get row count
            row_count = cursor.rowcount if cursor.rowcount >= 0 else 0
            self.connection.commit()
            logger.info(f"SQL query affected {row_count} rows")
            
            # Return a dict that will be properly converted to OutputData
            return {
                "rows": result,
                "metadata": {
                    "query": parameterized_query,
                    "row_count": row_count,
                    "columns": column_names,
                    "query_type": "SELECT" if cursor.description else "UPDATE/INSERT/DELETE"
                }
            }
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            # Return a dict that will be properly converted to OutputData
            # This ensures we return something that can be converted to OutputData
            return {
                "rows": [],
                "error": str(e),
                "metadata": {
                    "query": query,
                    "error_message": str(e)
                }
            }