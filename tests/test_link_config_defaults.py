import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
import logging

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import LinkConfig from base_link module
from links.base_link import LinkConfig, BaseLink
from links.llm_link import LLMLinkConfig, LLMLink
from links.sql_link import SQLLinkConfig, SQLLink
from links.user_input_link import UserInputLinkConfig, UserInputLink
from links.agent_link import AgentLinkConfig, AgentLink
from config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOKEN_LIMIT

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)

class TestLinkConfigDefaults(unittest.TestCase):
    """Test cases for LinkConfig default values and auto-type setting"""

    def test_user_input_link_defaults(self):
        """Test UserInputLinkConfig defaults"""
        # With explicit type
        config = UserInputLinkConfig(
            name="get_user_preferences",
            type="user_input"  # Explicitly set type
        )
        
        self.assertEqual(config.type, "user_input")
        self.assertEqual(config.name, "get_user_preferences")
        self.assertIsNone(config.inputs)
        self.assertIsNone(config.template)
        self.assertEqual(config.default_values, {})

        # With custom values
        default_values = {"favorite_color": "blue", "favorite_number": 42}
        config = UserInputLinkConfig(
            name="get_preferences",
            type="user_input",  # Explicitly set type
            default_values=default_values
        )
        
        self.assertEqual(config.type, "user_input")
        self.assertEqual(config.default_values, default_values)
    
    def test_sql_link_defaults(self):
        """Test SQLLinkConfig defaults"""
        from config import DATABASE_URL
        
        # With minimum parameters
        config = SQLLinkConfig(
            name="query_users",
            type="sql",  # Explicitly set type
            query="SELECT * FROM users"
        )
        
        self.assertEqual(config.type, "sql")
        self.assertEqual(config.query, "SELECT * FROM users")
        self.assertEqual(config.database_url, DATABASE_URL)  # Default from config
        
        # With custom values
        custom_db = "sqlite:///custom.db"
        config = SQLLinkConfig(
            name="query_products",
            type="sql",  # Explicitly set type
            query="SELECT * FROM products",
            database_url=custom_db
        )
        
        self.assertEqual(config.type, "sql")
        self.assertEqual(config.database_url, custom_db)
    
    def test_llm_link_defaults(self):
        """Test LLMLinkConfig defaults"""
        # With minimum parameters
        config = LLMLinkConfig(
            name="generate_text",
            type="llm",  # Explicitly set type
            prompt="Tell me about {topic}"
        )
        
        self.assertEqual(config.type, "llm")
        self.assertEqual(config.model, DEFAULT_LLM_MODEL)
        self.assertEqual(config.temperature, DEFAULT_TEMPERATURE)
        self.assertEqual(config.max_tokens, DEFAULT_TOKEN_LIMIT)
        self.assertEqual(config.output_key, "result")
        self.assertEqual(config.execution_method, "direct")
        
        # With custom values
        config = LLMLinkConfig(
            name="complex_prompt",
            type="llm",  # Explicitly set type
            template="my_template.txt",
            model="gpt-4-turbo",
            temperature=0.9,
            max_tokens=2000,
            output_key="custom_result",
            execution_method="chain"
        )
        
        self.assertEqual(config.type, "llm")
        self.assertEqual(config.model, "gpt-4-turbo")
        self.assertEqual(config.temperature, 0.9)
        self.assertEqual(config.max_tokens, 2000)
        self.assertEqual(config.output_key, "custom_result")
        self.assertEqual(config.execution_method, "chain")
        
        # Validate required fields - either prompt or template needed
        with self.assertRaises(ValueError):
            LLMLinkConfig(
                name="invalid_config"
                # Missing both prompt and template
            )
    
    def test_agent_link_defaults(self):
        """Test AgentLinkConfig defaults"""
        # With minimum parameters
        config = AgentLinkConfig(
            name="research_agent",
            type="agent",  # Explicitly set type
            task="Research quantum computing"
        )
        
        self.assertEqual(config.type, "agent")
        self.assertEqual(config.model, DEFAULT_LLM_MODEL)
        self.assertEqual(config.temperature, DEFAULT_TEMPERATURE)
        self.assertEqual(len(config.tools), 0)
        self.assertEqual(config.agent_type, "CONVERSATIONAL_REACT_DESCRIPTION")
        
        # With custom values
        tools = [{"name": "search", "type": "web", "description": "Search the web"}]
        config = AgentLinkConfig(
            name="custom_agent",
            type="agent",  # Explicitly set type
            task="Find information about {topic}",
            model="gpt-4",
            temperature=0.8,
            tools=tools,
            agent_type="ZERO_SHOT_REACT_DESCRIPTION"
        )
        
        self.assertEqual(config.type, "agent")
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.temperature, 0.8)
        self.assertEqual(len(config.tools), 1)
        self.assertEqual(config.tools[0]["name"], "search")
        self.assertEqual(config.agent_type, "ZERO_SHOT_REACT_DESCRIPTION")
    
    def test_link_validation_with_defaults(self):
        """Test validation of links with default values"""
        # Test SQL link
        sql_link = SQLLink()
        sql_config = SQLLinkConfig(name="test_query", type="sql", query="SELECT 1")
        
        # Should not raise any errors
        sql_link.validate_config(sql_config)
        
        # Test LLM link
        llm_link = LLMLink()
        llm_config = LLMLinkConfig(name="test_prompt", type="llm", prompt="Generate text")
        
        # Should not raise any errors
        llm_link.validate_config(llm_config)
        
        # Test agent link
        agent_link = AgentLink()
        agent_config = AgentLinkConfig(name="test_agent", type="agent", task="Research topic")
        
        # Should not raise any errors
        agent_link.validate_config(agent_config)
