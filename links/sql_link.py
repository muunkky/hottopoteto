import logging
import os
import sqlite3
from typing import Dict, Any, List, Optional, ClassVar
from pydantic import BaseModel, Field, field_validator
from langchain_community.utilities import SQLDatabase
from config import DATABASE_URL
from links.base_link import BaseLink, LinkConfig  # Import LinkConfig from base_link

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
        if database_url.startswith("sqlite:///"):
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
    
    def get_required_fields(self) -> list:
        """Returns list of required fields for SQL steps."""
        return ["name", "type", "query"]
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        if not config.query:
            raise ValueError("SQL step requires a 'query' field")
            
        if isinstance(config.query, str) and config.query.endswith(".sql"):
            try:
                self._validate_file_path(config.query)
            except ValueError as e:
                raise ValueError(f"SQL file validation error: {str(e)}")
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        step_name = config.name
        logging.info(f"🔍 Executing SQL step: {step_name}")
        
        query = config.query
        database_url = config.database_url or SQLLinkConfig.DEFAULT_DATABASE_URL
        
        if not query:
            raise ValueError("Query not found in configuration")
        
        if not self.connection:
            self._connect(database_url)
        
        if query.endswith(".sql"):
            logging.debug(f"Loading SQL from file: {query}")
            query_text = self.read_template_file(query)
            logging.debug(f"Loaded SQL query ({len(query_text)} chars)")
        else:
            query_text = query
            query_preview = query_text[:100] + ("..." if len(query_text) > 100 else "")
            logging.debug(f"Using inline SQL: {query_preview}")
        
        resolved_params = self.resolve_context_references(config.model_dump(), context)
        logging.debug(f"Resolved parameters from config: {resolved_params}")
        
        extracted = self.extract_parameters_from_template(query_text)
        logging.debug(f"Extracted parameters from query: {extracted}")
        for ref in extracted:
            if ref not in resolved_params:
                parts = ref.split('.')
                base = parts[0]
                if base in context:
                    value = context[base]
                    if isinstance(value, dict) and "data" in value:
                        if len(parts) > 1 and parts[1] == "data":
                            parts = [parts[0]] + parts[2:]
                        else:
                            value = value["data"]
                    for part in parts[1:]:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                            logging.debug(f"Accessed field '{part}': {value}")
                        else:
                            logging.error(f"Error: Could not resolve part '{part}' in reference '{ref}'")
                            value = None
                            break
                    if value is not None:
                        resolved_params[ref] = value
                        logging.debug(f"Resolved '{ref}' to: {value}")
                else:
                    logging.error(f"Base '{base}' not found in context for reference '{ref}'")
        logging.debug(f"Final resolved parameters: {resolved_params}")
        
        try:
            formatted_query = self.format_template_with_params(query_text, resolved_params)
            query_preview = formatted_query[:100] + ("..." if len(formatted_query) > 100 else "")
            logging.info(f"Executing SQL query: {query_preview}")
            logging.debug(f"Full SQL query: {formatted_query}")
        except ValueError as e:
            logging.error(f"❌ SQL query formatting error: {str(e)}")
            raise ValueError(f"SQL query formatting error: {str(e)}")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(formatted_query)
            result = cursor.fetchall()
            self.connection.commit()
            logging.info(f"SQL query returned {len(result)} rows")
            return {"result": result, "metadata": {"query": formatted_query, "row_count": len(result)}}
        except Exception as e:
            logging.error(f"❌ SQL execution error: {str(e)}")
            raise ValueError(f"SQL execution error: {str(e)}")