import logging
# chains/sequential_chain.py
from langchain_core.runnables.base import RunnableSequence
from chains.prompt_chain import execute_prompt_step
from chains.sql_chain import execute_sql_step
from chains.agent_chain import execute_agent_step
from utils.parameter_resolver import resolve_parameters


def build_sequential_chain(chains_list: list, input_variables: list):
    # NEW: Define a custom sequential executor with improved logging
    class SequentialChain:
        def __init__(self, chains):
            self.chains = chains

        def invoke(self, input_vars):
            current_vars = input_vars.copy()
            for chain in self.chains:
                logging.info(f"Executing chain: {chain.__class__.__name__} with input: {current_vars}")
                result = chain.invoke(current_vars)
                if not isinstance(result, dict):
                    logging.warning(f"{chain.__class__.__name__} returned non-dict output; wrapping result.")
                    result = {"result": result}
                logging.info(f"{chain.__class__.__name__} returned: {result}")
                current_vars.update(result)
            return current_vars

    return SequentialChain(chains_list)

def execute_recipe(recipe):
    context = {}  # Store step outputs
    for step in recipe:
        step_config = resolve_parameters(step, context)  # Inject dynamic values
        if step_config.get("type") == "prompt":
            output = execute_prompt_step(step_config, context)
        elif step_config.get("type") == "sql":
            output = execute_sql_step(step_config, context)
        elif step_config.get("type") == "agent":
            output = execute_agent_step(step_config, context)
        else:
            raise ValueError(f"Unknown step type: {step_config.get('type')}")
        
        # Ensure the output is stored in the context with the correct key
        context[f"{step_config.get('name').replace(' ', '_')}_output"] = output
    return context
