# PowerShell script to create a LangChain project structure
$projectRoot = "langchain-recipe-bot"

# Define directories
$directories = @(
    "$projectRoot/configs",
    "$projectRoot/prompts",
    "$projectRoot/chains",
    "$projectRoot/agents",
    "$projectRoot/database",
    "$projectRoot/utils"
)

# Define files
$files = @{
    "$projectRoot/configs/recipe_example.yaml" = @"
steps:
  - name: "Retrieve Customer Inquiry"
    type: "prompt"
    prompt: "step1_prompt.txt"
  - name: "Fetch Product Data"
    type: "sql"
    query: "step2_sql_query.txt"
  - name: "Summarize Response"
    type: "prompt"
    prompt: "step3_summary_template.txt"
    output_format: "json"
"@
    "$projectRoot/prompts/step1_prompt.txt" = "You are a helpful AI. Answer the following customer query:\n{{user_input}}"
    "$projectRoot/prompts/step2_sql_query.txt" = "SELECT * FROM products WHERE category = '{{category}}';"
    "$projectRoot/prompts/step3_summary_template.txt" = "Summarize the following information in less than 100 words:\n{{info}}"

    "$projectRoot/chains/prompt_chain.py" = "from langchain.chains import LLMChain\n# TODO: Implement prompt chain"
    "$projectRoot/chains/agent_chain.py" = "from langchain.agents import AgentExecutor\n# TODO: Implement agent chain"
    "$projectRoot/chains/sql_chain.py" = "from langchain.chains import SQLDatabaseChain\n# TODO: Implement SQL chain"
    "$projectRoot/chains/sequential_chain.py" = "from langchain.chains import SequentialChain\n# TODO: Implement sequential chaining"

    "$projectRoot/agents/function_calls.py" = "def custom_function():\n    return 'Custom function result'\n# TODO: Implement function calls"
    "$projectRoot/agents/agent_executor.py" = "from langchain.agents import initialize_agent\n# TODO: Implement agent executor"

    "$projectRoot/database/db_connection.py" = "from sqlalchemy import create_engine\n# TODO: Implement database connection"
    "$projectRoot/database/query_handler.py" = "def execute_query():\n    return 'Query result'\n# TODO: Implement query handling"

    "$projectRoot/utils/output_parser.py" = "from langchain.output_parsers import BaseOutputParser\n# TODO: Implement output parser"
    "$projectRoot/utils/config_loader.py" = "import yaml\n# TODO: Implement config loader"

    "$projectRoot/main.py" = "from langchain.llms import OpenAI\n# TODO: Implement main execution flow"
    "$projectRoot/requirements.txt" = "langchain\nopenai\npydantic\nsqlalchemy"
    "$projectRoot/README.md" = "# LangChain Recipe-Based Bot\nThis project implements prompt chaining with LangChain."
    "$projectRoot/.env" = "OPENAI_API_KEY=your-api-key-here"
}

# Create directories
foreach ($dir in $directories) {
    if (!(Test-Path -Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
}

# Create files with content
foreach ($file in $files.Keys) {
    if (!(Test-Path -Path $file)) {
        $files[$file] | Out-File -FilePath $file -Encoding utf8
    }
}

Write-Host "✅ LangChain project structure created successfully!"
