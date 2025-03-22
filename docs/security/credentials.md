# Credential Management in Hottopoteto

This document explains how to securely manage credentials in Hottopoteto.

## Overview

Hottopoteto requires access to various services and APIs that need authentication. This guide explains how to securely manage credentials for these services.

## Principles

1. **Never store credentials in code or recipe files**
2. **Never commit credentials to version control**
3. **Use environment variables for secure access**
4. **Provide clear instructions for required credentials**

## Environment Variables

Hottopoteto uses environment variables to access sensitive information like API keys. You can set these variables in several ways:

### Using .env Files (Recommended)

Hottopoteto supports hierarchical .env files:

1. **Domain-specific files**: `core/domains/<domain>/.env.<domain>`
2. **Core settings file**: `core/.env.core`
3. **Root .env file**: `.env` (in project root)

The system loads these files in the order listed above, with later files overriding earlier ones. This allows you to:
- Keep domain-specific credentials separate
- Override specific credentials in the root .env
- Organize credentials based on their usage

Example `.env` file:
```
# API Keys
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/db
```

### Using Environment Variables Directly

Set environment variables in your terminal:

```bash
# In Bash/Shell
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=AIza...

# In Windows Command Prompt
set OPENAI_API_KEY=sk-...
set GEMINI_API_KEY=AIza...

# In PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:GEMINI_API_KEY="AIza..."
```

## Accessing Credentials in Code

Hottopoteto provides a secure way to access credentials:

```python
from core.security import get_credential

# Get a credential with a default fallback
api_key = get_credential("OPENAI_API_KEY", default=None)

# Get a credential for a specific domain
gemini_key = get_credential("GEMINI_API_KEY", domain="llm")

# Get a credential with validation
db_url = get_credential("DATABASE_URL", validator=lambda x: x.startswith("postgresql://"))
```

## Accessing Credentials in Recipes

In recipes, use the `env()` function to access credentials:

```yaml
- name: "API_Request"
  type: "http"
  url: "https://api.example.com/data"
  headers:
    Authorization: "Bearer {{ env('API_KEY') }}"
```

## Credential Management Commands

Hottopoteto provides commands to manage credentials:

```bash
# List required credentials
python main.py credentials list

# Check if all required credentials are set
python main.py credentials check

# Set a credential (interactive)
python main.py credentials set CREDENTIAL_NAME
```

## Required Credentials by Domain

Different domains require different credentials:

### LLM Domain
- `OPENAI_API_KEY`: For OpenAI models
- `GEMINI_API_KEY`: For Google Gemini models
- `ANTHROPIC_API_KEY`: For Anthropic models

### Storage Domain
- `DATABASE_URL`: For database connections
- `MONGODB_URI`: For MongoDB connections
- `AWS_ACCESS_KEY_ID`: For AWS S3 storage
- `AWS_SECRET_ACCESS_KEY`: For AWS S3 storage

### HTTP Domain
- Domain-specific API keys as needed

## Handling Missing Credentials

When a credential is missing, Hottopoteto:

1. Logs a warning
2. Attempts to use a fallback if provided
3. Raises a `MissingCredentialError` if no fallback is available

You can handle missing credentials with try/except blocks:

```python
try:
    api_key = get_credential("API_KEY", required=True)
except MissingCredentialError:
    # Handle missing credential
    print("Please set the API_KEY credential")
    sys.exit(1)
```

## Best Practices

1. **Use domain-specific prefixes**: Prefix credentials with domain names to avoid conflicts
2. **Document required credentials**: Include a list of required credentials in your documentation
3. **Provide clear instructions**: Explain how to obtain and set required credentials
4. **Validate credentials**: Check credential format and validity before use
5. **Handle missing credentials gracefully**: Provide clear error messages when credentials are missing
6. **Manage permissions carefully**: Only request the permissions your application needs

## Security Considerations

1. **Environment variables**: Environment variables can be leaked through process listings on shared systems
2. **.env files**: .env files should have restricted permissions (e.g., chmod 600)
3. **Memory protection**: Credentials in memory should be treated as sensitive data
4. **Logging**: Never log credentials or include them in error messages
5. **Rotation**: Consider credential rotation for long-lived deployments
