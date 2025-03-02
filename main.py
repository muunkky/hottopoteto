# main.py
import os
from utils.config_loader import load_config
from chains.prompt_chain import build_prompt_chain
from chains.agent_chain import build_agent_chain
from chains.sql_chain import build_sql_chain
from chains.sequential_chain import build_sequential_chain

def main():
    # Load the recipe configuration from the YAML file
    recipe_config = load_config("configs/recipe_example.yaml")
    steps = recipe_config.get("steps", [])
    
    # List to hold individual chain objects for each step
    chains_list = []
    
    # Example initial input variables (could be dynamically set)
    input_variables = {"user_input": "example word"}
    
    # Build the chain for each step based on its type
    for step in steps:
        step_type = step.get("type")
        if step_type == "prompt":
            chain = build_prompt_chain(step)
        elif step_type == "sql":
            chain = build_sql_chain(step)
        elif step_type == "agent":
            chain = build_agent_chain(step)
        else:
            raise ValueError(f"Unsupported step type: {step_type}")
        
        chains_list.append(chain)
    
    # Build a SequentialChain to execute all steps in order
    sequential_chain = build_sequential_chain(chains_list, list(input_variables.keys()))
    
    # Run the sequential chain with the initial input variables
    result = sequential_chain.run(input_variables)
    
    print("Final Result:")
    print(result)

if __name__ == "__main__":
    main()
