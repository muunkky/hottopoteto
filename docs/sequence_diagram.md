# Recipe Execution Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Main as main.py
    participant RecipeLoader as utils/recipe_loader.py
    participant SeqChain as chains/sequential_chain.py
    participant PromptChain as chains/prompt_chain.py
    participant SQLChain as chains/sql_chain.py
    participant AgentChain as chains/agent_chain.py
    participant InteractiveInput as utils/interactive_input.py
    
    User->>Main: python main.py -r ice_cream_recipe.yaml
    activate Main
    
    Main->>RecipeLoader: load_recipe("recipes/ice_cream_recipe.yaml")
    activate RecipeLoader
    RecipeLoader-->>Main: recipe (list of step dicts)
    deactivate RecipeLoader
    
    Main->>SeqChain: execute_recipe(recipe)
    activate SeqChain
    
    loop For each step in recipe
        SeqChain->>SeqChain: resolve_parameters(step, context)
        
        alt step_type == "prompt"
            SeqChain->>PromptChain: execute_prompt_step(step_dict, context)
            activate PromptChain
            PromptChain-->>SeqChain: output (dict or str)
            deactivate PromptChain
        else step_type == "sql"
            SeqChain->>SQLChain: execute_sql_step(step_dict, context)
            activate SQLChain
            SQLChain-->>SeqChain: output (query results)
            deactivate SQLChain
        else step_type == "agent"
            SeqChain->>AgentChain: execute_agent_step(step_dict, context)
            activate AgentChain
            AgentChain-->>SeqChain: output (agent results)
            deactivate AgentChain
        else step_type == "interactive_input"
            SeqChain->>InteractiveInput: execute_interactive_input_step(step_dict, context)
            activate InteractiveInput
            InteractiveInput->>User: Request input
            User-->>InteractiveInput: Provide input
            InteractiveInput-->>SeqChain: output (user input)
            deactivate InteractiveInput
        end
        
        SeqChain->>SeqChain: context[step_name + "_output"] = output
    end
    
    SeqChain-->>Main: context (all step outputs)
    deactivate SeqChain
    
    Main->>Main: Log final results
    Main-->>User: Display results
    deactivate Main
```

## Flow Explanation

1. **User Initiates**: The user runs the application with a recipe file argument.
2. **Recipe Loading**: `main.py` calls `load_recipe()` to parse the YAML file into a list of step dictionaries.
3. **Recipe Execution**: The parsed recipe is passed to `execute_recipe()` in `sequential_chain.py`.
4. **Step Processing Loop**: For each step in the recipe:
   - **Parameter Resolution**: Placeholders like `{{previous_step_output.field}}` are replaced with actual values.
   - **Step Type Selection**: Based on the step type, the appropriate execution function is called.
   - **Context Update**: The output of each step is stored in the context dictionary with the key `{step_name}_output`.
5. **Final Results**: After all steps are executed, the complete context is returned to `main.py` which logs the results.
