# Key Functions in Recipe Execution Flow

This document outlines the key functions involved in the `execute` command flow, providing a description of their purpose, inputs, and outputs.

## 1. `main` (lexicon/main.py)

*   **Purpose:** Entry point for the CLI application. Handles command-line argument parsing and calls the appropriate functions based on the command.
*   **Inputs:**
    *   `args`: Parsed command-line arguments (e.g., `recipe_file`, `origin_language`, `part_of_speech`).
*   **Outputs:**
    *   Prints messages to the console indicating the success or failure of the command.
    *   Calls other functions to perform the requested action.

## 2. `LexiconManager.create_word_from_recipe` (lexicon/manager.py)

*   **Purpose:** Creates a word entry from the output of a recipe and adds it to the lexicon.
*   **Inputs:**
    *   `recipe_output`: A dictionary containing the output of the recipe execution.
*   **Outputs:**
    *   `word_id`: The ID of the newly created word.

## 3. `WordEntryModel.from_recipe_output` (lexicon/models/word.py)

*   **Purpose:** Transforms the recipe output into a `WordEntryModel` instance.
*   **Inputs:**
    *   `recipe_output`: A dictionary containing the output of the recipe execution.
*   **Outputs:**
    *   `word_entry`: An instance of `WordEntryModel` representing the new word.

## 4. `LexiconManager.add_word` (lexicon/manager.py)

*   **Purpose:** Adds a word to the lexicon, performing schema validation and indexing.
*   **Inputs:**
    *   `word_entry`: A dictionary or `WordEntryModel` instance representing the word to be added.
    *   `validate`: A boolean indicating whether to perform schema validation.
*   **Outputs:**
    *   `word_id`: The ID of the newly added word.

## 5. `RecipeExecutor.execute` (core/executor.py)

*   **Purpose:** Executes the recipe step-by-step, collecting user input and generating the final output.
*   **Inputs:**
    *   `recipe_file`: The path to the YAML or JSON recipe file.
*   **Outputs:**
    *   `recipe_output`: A dictionary containing the output of each step in the recipe.

## 6. `DomainProcessor.process_recipe_output` (domains/conlang/\_\_init\_\_.py)

*   **Purpose:** Processes the recipe output into a format suitable for creating a word entry.
*   **Inputs:**
    *   `recipe_output`: A dictionary containing the output of the recipe execution.
*   **Outputs:**
    *   `word_entry`: A dictionary or `WordEntryModel` instance representing the new word.


```mermaid
sequenceDiagram
    participant User
    participant main.py
    participant RecipeProcessor
    participant LexiconManager
    participant RecipeExecutor
    participant LLM
    participant WordEntryModel

    User->>main.py: python main.py execute --recipe_file recipes\conlang\eldorian_word.yaml
    main.py->>RecipeProcessor: recipe_processor = RecipeProcessor(lexicon_dir="lexicon")
    main.py->>RecipeProcessor: new_word_id = recipe_processor.execute_recipe(args.recipe_file)
    RecipeProcessor->>RecipeProcessor: with open(recipe_file)
    RecipeProcessor->>RecipeExecutor: executor = RecipeExecutor(recipe_file)
    RecipeExecutor->>RecipeExecutor: with open(recipe_file)
    RecipeExecutor->>RecipeExecutor: self.recipe = yaml.safe_load(f)
    RecipeExecutor->>RecipeExecutor: self._init_handlers()
    RecipeExecutor->>RecipeExecutor: self.env = Environment(...)
    RecipeExecutor->>RecipeExecutor: self.memory = {}
    RecipeExecutor->>RecipeExecutor: self.function_registry = {...}
    RecipeExecutor->>RecipeExecutor: self.function_registry.update(domain_functions)
    RecipeExecutor->>RecipeExecutor: links = self.recipe.get("links", [])
    RecipeExecutor->>RecipeExecutor: for link_name, link_config in links_dict.items()
    loop For each link
        alt link_type == "llm"
            RecipeExecutor->>LLM: formatted_prompt = self._get_formatted_prompt(link_config, self.memory)
            RecipeExecutor->>LLM: llm = ChatOpenAI(...)
            RecipeExecutor->>LLM: response = llm.invoke(formatted_prompt)
            LLM-->>RecipeExecutor: raw_result = response.content
            RecipeExecutor->>RecipeExecutor: link_output = LLMOutput(raw=raw_result, data={...})
        else link_type == "function"
            RecipeExecutor->>RecipeExecutor: inputs = self._process_function_inputs(link_config)
            RecipeExecutor->>RecipeExecutor: result = self.function_registry[function_name](**inputs)
            RecipeExecutor->>RecipeExecutor: link_output = FunctionOutput(data=result)
        else link_type == "user_input"
            RecipeExecutor->>User: Prompt user for input
            User-->>RecipeExecutor: user_input
            RecipeExecutor->>RecipeExecutor: link_output = UserInputOutput(data=user_input)
        end
        RecipeExecutor->>RecipeExecutor: self.memory[link_name] = link_output
    end
    RecipeExecutor->>RecipeExecutor: processor = get_domain_processor(self.domain)
    RecipeExecutor->>RecipeExecutor: recipe_output = processor.process_recipe_output(self.memory)
    RecipeProcessor->>LexiconManager: new_word_id = self.lexicon_manager.create_word_from_recipe(recipe_output)
    LexiconManager->>WordEntryModel: word_entry = WordEntryModel.from_recipe_output(recipe_output)
    LexiconManager->>LexiconManager: word_id = self.add_word(word_entry)
    LexiconManager-->>RecipeProcessor: new_word_id
    RecipeProcessor-->>main.py: new_word_id
    main.py->>User: Executed recipe, new word ID: {new_word_id}
```