# chains/agent_chain.py
from langchain.agents import initialize_agent, Tool
from langchain_community.llms import OpenAI

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
