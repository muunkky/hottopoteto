# chains/sequential_chain.py
from langchain.chains import SequentialChain

def build_sequential_chain(chains_list: list, input_variables: list) -> SequentialChain:
    """
    Build a SequentialChain that connects multiple chains sequentially.
    
    Args:
        chains_list (list): List of chain objects (prompt, agent, sql, etc.).
        input_variables (list): List of variable names to be passed from the initial input.
    
    Returns:
        SequentialChain: A chain that runs the provided chains sequentially.
    """
    sequential_chain = SequentialChain(
        chains=chains_list, 
        input_variables=input_variables, 
        verbose=True
    )
    return sequential_chain
