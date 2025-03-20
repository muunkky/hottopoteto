# CLI Commands Reference

This document provides a comprehensive reference for all command-line interface (CLI) commands available in Hottopoteto.

## Global Options

These options can be used with any command:

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug-level logging |
| `--trace` | Enable trace-level logging (more detailed than debug) |
| `--quiet` | Suppress all output except warnings and errors |
| `--help` | Display help information for a command |
| `--version` | Display version information |
| `--config FILE` | Specify a configuration file |

## Main Commands

### execute

Execute a recipe from a file.

```bash
python main.py execute --recipe_file PATH [OPTIONS]
```

**Options:**
- `--recipe_file PATH`: Path to recipe file (required)
- `--output_dir PATH`: Directory to save outputs (default: "output")
- `--variables KEY=VALUE`: Set variables (can be used multiple times)
- `--format FORMAT`: Output format (default: text)

**Example:**
```bash
python main.py execute --recipe_file recipes/my_recipe.yaml --variables name=John
```

### domains

Commands for working with domains.

#### list

List available domains.

```bash
python main.py domains list
```

#### info

Show information about a domain.

```bash
python main.py domains info DOMAIN_NAME
```

**Example:**
```bash
python main.py domains info conlang
```

#### packages

List packages that implement a domain.

```bash
python main.py domains packages DOMAIN_NAME
```

**Example:**
```bash
python main.py domains packages llm
```

### plugins

Commands for working with plugins.

#### list

List available plugins.

```bash
python main.py plugins list
```

#### info

Show information about a plugin.

```bash
python main.py plugins info PLUGIN_NAME
```

**Example:**
```bash
python main.py plugins info gemini
```

### packages

Commands for working with packages.

#### list

List installed packages.

```bash
python main.py packages list
```

#### install

Install a package.

```bash
python main.py packages install PACKAGE_NAME [OPTIONS]
```

**Options:**
- `--dev`: Install in development mode

**Example:**
```bash
python main.py packages install hottopoteto-linguistics
```

#### uninstall

Uninstall a package.

```bash
python main.py packages uninstall PACKAGE_NAME
```

**Example:**
```bash
python main.py packages uninstall hottopoteto-linguistics
```

#### create

Create a new package template.

```bash
python main.py packages create NAME [OPTIONS]
```

**Options:**
- `--domain DOMAIN`: Include a domain template
- `--plugin PLUGIN`: Include a plugin template

**Example:**
```bash
python main.py packages create my_package --domain my_domain --plugin my_plugin
```

### validate

Validate a recipe without executing it.

```bash
python main.py validate --recipe_file PATH
```

**Example:**
```bash
python main.py validate --recipe_file recipes/my_recipe.yaml
```

### schema

Commands for working with schemas.

#### list

List available schemas.

```bash
python main.py schema list [DOMAIN_NAME]
```

**Example:**
```bash
python main.py schema list conlang
```

#### show

Show the definition of a schema.

```bash
python main.py schema show DOMAIN_NAME.SCHEMA_NAME
```

**Example:**
```bash
python main.py schema show conlang.word
```

## Advanced Usage

### Using Environment Variables

Many CLI options can also be configured using environment variables:

```bash
# Set default output directory
export HOTTOPOTETO_OUTPUT_DIR=my_outputs

# Set log level
export HOTTOPOTETO_LOG_LEVEL=DEBUG

# Run a command
python main.py execute --recipe_file my_recipe.yaml
```

### Piping and Redirection

The CLI supports standard Unix piping and redirection:

```bash
# Redirect output to a file
python main.py execute --recipe_file my_recipe.yaml > output.txt

# Pipe output to another program
python main.py domains list | grep conlang
```

### Exit Codes

The CLI uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid argument
- `3`: Environment error
- `4`: Recipe execution error
- `5`: Plugin error

### Interactive Mode

Some commands support interactive mode:

```bash
# Start interactive mode
python main.py interactive
```

In interactive mode, you can:
- Execute recipes
- Inspect context
- Debug recipe execution
- Step through links

### Script Mode

Create executable recipe scripts:

```bash
#!/usr/bin/env python
# file: my_script.py
import hottopoteto
hottopoteto.run_recipe("recipes/my_recipe.yaml")
```

Make executable:

```bash
chmod +x my_script.py
./my_script.py
```
