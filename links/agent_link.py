import logging
import os
from typing import Dict, Any, Optional, List, Callable, ClassVar
from pydantic import BaseModel, Field, field_validator
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from config import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE
from links.base_link import BaseLink, LinkConfig  # Import LinkConfig from base_link

class ToolConfig(BaseModel):
    """Configuration model for agent tools"""
    name: str
    description: Optional[str] = ""
    type: str
    code: Optional[str] = None

class AgentLinkConfig(LinkConfig):
    """Extended configuration for agent link with specific fields"""
    # Default constants
    DEFAULT_TYPE: ClassVar[str] = "agent"
    DEFAULT_MODEL: ClassVar[str] = DEFAULT_LLM_MODEL
    DEFAULT_TEMPERATURE: ClassVar[float] = DEFAULT_TEMPERATURE
    DEFAULT_AGENT_TYPE: ClassVar[str] = "CONVERSATIONAL_REACT_DESCRIPTION"
    
    # Required fields
    task: str
    
    # Optional fields with defaults
    model: str = Field(default_factory=lambda: AgentLinkConfig.DEFAULT_MODEL)
    temperature: float = Field(default_factory=lambda: AgentLinkConfig.DEFAULT_TEMPERATURE)
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    agent_type: str = Field(default_factory=lambda: AgentLinkConfig.DEFAULT_AGENT_TYPE)
    
    # Auto-set type if not provided
    @field_validator('type', mode='before')
    @classmethod
    def set_default_type(cls, v):
        return v or cls.DEFAULT_TYPE

class AgentLink(BaseLink):
    """Link for executing LangChain agents with tools."""
    
    # Mapping from string to AgentType enum values
    AGENT_TYPE_MAP = {
        "ZERO_SHOT_REACT_DESCRIPTION": AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        "REACT_DOCSTORE": AgentType.REACT_DOCSTORE,
        "SELF_ASK_WITH_SEARCH": AgentType.SELF_ASK_WITH_SEARCH,
        "CONVERSATIONAL_REACT_DESCRIPTION": AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        "CHAT_ZERO_SHOT_REACT_DESCRIPTION": AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        "STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION": AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    }
    
    def get_required_fields(self) -> list:
        """Returns list of required fields for agent steps."""
        return ["name", "type", "task"]
    
    def _validate_config_impl(self, config: LinkConfig) -> None:
        """
        Validate agent link configuration.
        
        Args:
            config: The LinkConfig object to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not config.task:
            raise ValueError("Agent step requires a 'task' field")
    
        # Validate agent_type if present
        if config.agent_type and config.agent_type not in self.AGENT_TYPE_MAP:
            valid_types = list(self.AGENT_TYPE_MAP.keys())
            raise ValueError(f"Invalid agent_type '{config.agent_type}'. Valid types: {valid_types}")
    
    def _execute_impl(self, config: LinkConfig, context: Dict[str, Any]) -> Any:
        """
        Execute an agent with tools.
        
        Args:
            config: The LinkConfig object for this step
            context: Current execution context
            
        Returns:
            The agent execution results
        """
        step_name = config.name
        logging.info(f"🤖 Executing agent step: {step_name}")
        
        task = config.task
        model_name = config.model or AgentLinkConfig.DEFAULT_MODEL
        temperature = config.temperature or AgentLinkConfig.DEFAULT_TEMPERATURE
        agent_type_str = config.agent_type or AgentLinkConfig.DEFAULT_AGENT_TYPE
        tools_config = config.tools or []
        
        # Map string agent types to LangChain AgentType enum
        agent_type = self.AGENT_TYPE_MAP.get(agent_type_str, AgentType.CONVERSATIONAL_REACT_DESCRIPTION)
        logging.debug(f"Using agent type: {agent_type}")
        
        # Resolve parameters from context
        logging.debug("Resolving agent parameters from context")
        resolved_params = self.resolve_context_references(config.model_dump(), context)
        logging.debug(f"Resolved parameters: {resolved_params}")
        
        # Format task if it contains parameter placeholders
        if isinstance(task, str):
            try:
                task = self.format_template_with_params(task, resolved_params)
                logging.debug(f"Formatted task: {task}")
            except ValueError as e:
                logging.error(f"❌ Error formatting task: {str(e)}")
                raise ValueError(f"Error formatting task: {str(e)}")
        
        # Create LLM
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
        # Process tools configuration
        tools = self._create_tools(tools_config, context)
        logging.debug(f"Created {len(tools)} tools for agent")
        
        # Create agent
        try:
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=agent_type,
                verbose=True
            )
            
            logging.info(f"Running agent with task: {task}")
            result = agent.run(task)
            logging.info(f"Agent execution completed")
            
            # Add metadata
            metadata = {
                "model": model_name,
                "temperature": temperature,
                "agent_type": agent_type_str,
                "tools_used": [tool.name for tool in tools]
            }
            
            return {"result": result, "metadata": metadata}
            
        except Exception as e:
            logging.error(f"Agent execution failed: {str(e)}")
            raise ValueError(f"Agent execution failed: {str(e)}")
    
    def _create_tools(self, tools_config: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Tool]:
        """Create LangChain tools from configuration."""
        tools = []
        
        for tool_config in tools_config:
            tool_name = tool_config.get("name")
            tool_description = tool_config.get("description", "")
            tool_type = tool_config.get("type")
            
            if not tool_name or not tool_type:
                logging.warning(f"Skipping tool with missing name or type: {tool_config}")
                continue
            
            try:
                if tool_type == "function":
                    # Function-based tool
                    tool_function = self._get_tool_function(tool_config, context)
                    tools.append(
                        Tool(
                            name=tool_name,
                            description=tool_description,
                            func=tool_function
                        )
                    )
                elif tool_type == "search":
                    # Search-based tool (e.g., web search)
                    from langchain_community.utilities import GoogleSearchAPIWrapper
                    search = GoogleSearchAPIWrapper()
                    tools.append(
                        Tool(
                            name=tool_name,
                            description=tool_description,
                            func=search.run
                        )
                    )
                elif tool_type == "web":
                    # Web-based tool
                    from langchain_community.utilities import GoogleSerperAPIWrapper
                    search = GoogleSerperAPIWrapper()
                    tools.append(
                        Tool(
                            name=tool_name,
                            description=tool_description,
                            func=search.run
                        )
                    )
                else:
                    logging.warning(f"Unknown tool type: {tool_type}")
                    
            except Exception as e:
                logging.error(f"Error creating tool '{tool_name}': {str(e)}")
                
        return tools
    
    def _get_tool_function(self, tool_config: Dict[str, Any], context: Dict[str, Any]) -> Callable:
        """Create a function for a function-based tool."""
        # Extract function body/code
        code = tool_config.get("code", "")
        if not code:
            raise ValueError(f"Tool {tool_config.get('name')} has no code")
        
        # Create a function from the code
        # WARNING: This uses eval which can be a security risk if configurations come from untrusted sources
        # Consider a safer alternative in production
        def tool_function(input_text):
            # Create local namespace with context variables
            local_vars = {
                "input": input_text,
                "context": context
            }
            
            try:
                # Execute the code with the local namespace
                exec(code, globals(), local_vars)
                # Return the result variable if defined
                if "result" in local_vars:
                    return local_vars["result"]
                else:
                    return "Tool executed but no result was returned."
            except Exception as e:
                return f"Error executing tool: {str(e)}"
        
        return tool_function