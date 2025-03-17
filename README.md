# Hottopoteto

Hottopoteto is a flexible framework for building AI-powered applications through composable recipes. It allows you to connect various AI components, data sources, and tools to create powerful workflows.

## 🌟 Key Features

- **Domain-Based Architecture**: Specialized support for different knowledge domains
- **Plugin System**: Extend functionality with plugins for various services and tools
- **Package Management**: Add new domains and plugins through installable packages
- **Recipe-Driven**: Define workflows as recipes with a declarative YAML format
- **Storage Adapters**: Flexible storage options for persisting data
- **Schema Validation**: Built-in schema validation for consistent data structures

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/muunkky/Hottopoteto.git
cd hottopoteto

# Install dependencies
pip install -r requirements.txt
```

### Running Your First Recipe

```bash
# Execute a sample recipe
python main.py execute --recipe_file recipes/examples/gemini_example.yaml
```

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

## 📚 Documentation

For more detailed documentation:

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Creating Plugins](docs/guides/creating_plugins.md)
- [Creating Domains](docs/guides/creating_domains.md)
- [Package Management](docs/packages.md)
- [Recipe Reference](docs/reference/recipes.md)
- [Link Types Reference](docs/reference/link_types.md)

## 🤝 Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md) for more information.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
