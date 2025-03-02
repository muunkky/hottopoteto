# agents/agent_executor.py
def execute_agent(agent, input_data: dict):
    """
    Execute the provided agent with the given input data.
    
    Args:
        agent: The agent instance to execute.
        input_data (dict): Input parameters for the agent.
    
    Returns:
        The output produced by the agent.
    """
    return agent.run(input_data)
