# Hottopoteto

Hottopoteto is a flexible framework for building AI-powered applications through composable recipes. It allows you to connect various AI components, data sources, and tools to create powerful workflows.

## 🌟 Key Features

- **Domain-Based Architecture**: Specialized support for different knowledge domains
- **Plugin System**: Extend functionality with plugins for various services and tools
- **Package Management**: Add new domains and plugins through installable packages
- **Recipe-Driven**: Define workflows as recipes with a declarative YAML format
- **Storage Adapters**: Flexible storage options for persisting data
- **Schema Validation**: Built-in schema validation for consistent data structures

## 🎯 Who Is Hottopoteto For?

- **AI Developers**: Build complex AI workflows with minimal boilerplate code
- **Data Scientists**: Create data processing pipelines with LLM integration
- **Automation Engineers**: Design automated workflows that combine AI services
- **Content Creators**: Assemble content generation pipelines with fine-tuned control
- **Domain Experts**: Implement specialized tools in areas like linguistics or storytelling
- **No-Code Enthusiasts**: Create powerful AI applications through YAML configuration

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/muunkky/hottopoteto.git
cd hottopoteto

# Install dependencies
pip install -r requirements.txt
```

### Running Your First Recipe

```bash
# Execute a sample recipe
python main.py execute --recipe_file recipes/examples/gemini_example.yaml
```

## 💼 Example Use Cases

- **Content Generation**: Create multi-stage content generation pipelines with LLM refinement
- **Knowledge Management**: Build systems that analyze, organize, and query information
- **Conlang Creation**: Generate constructed languages with rich linguistic features
- **Interactive Stories**: Create interactive narrative experiences with branching pathways
- **Custom AI Assistants**: Design specialized assistants with domain-specific knowledge
- **Data Processing**: Build workflows that collect, process, and analyze diverse data sources

## 📋 Core Concepts

### Recipes

Recipes are YAML files that define a sequence of operations (links) to execute:

```yaml
name: "Hello World Recipe"
description: "A simple example recipe"
version: "1.0"
links:
  - name: "User_Input"
    type: "user_input"
    description: "Get user name"
    inputs:
      name:
        type: "string"
        description: "Your name"
    
  - name: "Greeting"
    type: "llm"
    model: "gpt-4o"
    prompt: "Write a greeting for {{ User_Input.data.name }}."
```

### Domains

Domains represent specialized knowledge areas with their own data models, schemas, and utilities:

```bash
# List available domains
python main.py domains list

# Get information about a domain
python main.py domains info conlang
```

### Plugins

Plugins add new link types and functionality:

```bash
# List available plugins
python main.py plugins list

# Get information about a plugin
python main.py plugins info gemini
```

## 🧠 Core Principles

Hottopoteto follows these key architectural principles:

1. **Domain Isolation**: Links operate within a single domain to ensure clean separation
2. **Cross-Domain Communication**: Only core infrastructure enables cross-domain interaction
3. **Secure Credential Management**: API keys and credentials are never stored in code
4. **Recipe Composition**: Recipes orchestrate functionality across domains
5. **Plugin Extensibility**: The system can be extended without modifying core code

For more details, see our [Core Principles](docs/core/principles.md) documentation.

## 🧪 Testing

Hottopoteto uses pytest for testing with comprehensive coverage reporting.

### Running Tests

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate      # Linux/Mac

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_executor.py

# Run tests with coverage report
pytest --cov=core --cov=plugins --cov-report=html

# Run tests by marker
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
```

### Test Organization

- `tests/unit/` - Fast, isolated unit tests
- `tests/integration/` - Integration tests requiring external resources
- `tests/conftest.py` - Shared fixtures and test configuration

### Coverage

Current test coverage baseline: **8%**

View detailed coverage reports:
```bash
# Generate HTML coverage report
pytest --cov=core --cov=plugins --cov-report=html

# Open the report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```

## 📚 Documentation

For more detailed documentation:

- [Architecture Overview](ARCHITECTURE.md)
- [Core Principles](docs/core/principles.md)
- [Creating Plugins](docs/guides/creating_plugins.md)
- [Creating Domains](docs/DOMAIN_STRUCTURE.md)
- [Package Management](docs/packages.md)
- [Recipe Execution](docs/recipe_execution.md)
- [Security & Credentials](docs/security/credentials.md)
- [Reference Documentation](docs/reference/)

## 🤝 Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md) for more information.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
