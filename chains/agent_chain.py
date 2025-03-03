# chains/agent_chain.py
from langchain.agents import initialize_agent, Tool
from langchain_openai import OpenAI
import importlib.util
import re

def load_function_from_path(path, function_name):
    module_name = path.replace("/", ".").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)  # Dynamically get the function by name

def extract_value_from_context(placeholder, context):
    """Extract value from context based on a placeholder string like '{{Step2_output.data}}'"""
    placeholder = placeholder.strip("{}")  # Remove {{ }}
    parts = placeholder.split(".")
    
    # If it's a direct key in context
    if len(parts) == 1 and parts[0] in context:
        return context[parts[0]]
    
    # If it's a nested key like Step2_output.data
    if len(parts) > 1 and parts[0] in context:
        obj = context[parts[0]]
        for part in parts[1:]:
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                # If value is a string, just return it directly as fallback
                return obj
        return obj
    
    # Default case - return the original placeholder
    return placeholder

def execute_agent_step(step_config, context):
    function_name = step_config.get("function_name", "custom_function") 
    agent_function = load_function_from_path(step_config["function"], function_name)
    
    # Extract parameters using placeholder resolution
    function_params = {}
    for key, value in step_config.get("parameters", {}).items():
        # Check if value is a placeholder
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            function_params[key] = extract_value_from_context(value, context)
        else:
            function_params[key] = value
    
    return agent_function(**function_params)

def build_agent_chain(step_config: dict):
    """
    Build an agent chain for an 'agent' step that executes an external function.
    
    Args:
        step_config (dict): Dictionary containing the step configuration from YAML.
    
    Returns:
        A configured agent executor.
    """
    # For demonstration, import a custom function from the agents module.
    from agents.function_calls import custom_function

    # Wrap the function as a Tool for the agent.
    tool = Tool(
        name="custom_function",
        func=custom_function,
        description="A custom function to process data."
    )

    # Initialize the LLM for the agent.
    llm = OpenAI(temperature=0.7)
    
    # Initialize the agent with the provided tool.
    agent = initialize_agent(
        tools=[tool],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    return agent
