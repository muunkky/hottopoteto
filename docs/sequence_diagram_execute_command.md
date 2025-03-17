# Recipe Execution Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant RecipeExecutor
    participant DomainProcessor
    participant Repository

    User->>Main: python main.py execute --recipe_file recipes/conlang/eldorian_word.yaml
    Main->>RecipeExecutor: executor = RecipeExecutor(recipe_file)
    
    RecipeExecutor->>RecipeExecutor: Load and parse recipe YAML
    
    loop For each link in recipe
        alt link_type == "user_input"
            RecipeExecutor->>User: Prompt for input
            User->>RecipeExecutor: Provide input
        else link_type == "llm"
            RecipeExecutor->>RecipeExecutor: Format prompt
            RecipeExecutor->>LLM: Send prompt
            LLM->>RecipeExecutor: Return response
        else link_type == "function"
            RecipeExecutor->>RecipeExecutor: Process inputs
            RecipeExecutor->>RecipeExecutor: Execute function
        end
        RecipeExecutor->>RecipeExecutor: Store result in memory
    end

    RecipeExecutor->>DomainProcessor: process_recipe_output(result)
    DomainProcessor->>RecipeExecutor: Return processed entry
    
    alt --output_dir specified
        Main->>Main: Save output to file
    end
    
    Main->>User: Print success message
```

This diagram illustrates the flow of execution when running the `execute` command. The RecipeExecutor processes each link in the recipe, which can be one of three types:

1. **user_input**: Prompts the user for input and stores the result
2. **llm**: Sends a prompt to an LLM model and processes the response
3. **function**: Executes a function with specified inputs

After all links are processed, the result is passed to a domain-specific processor to transform it into a domain-specific model or data structure. If an output directory is specified, the result is also saved to a file.
