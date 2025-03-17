# Creating Plugins for LangChain V2

This guide explains how to create plugins for LangChain V2 to extend its functionality with new link types, utilities, and integrations.

## Plugin Structure

A plugin consists of the following components:

1. **Manifest**: Metadata about the plugin
2. **Link Handlers**: Classes that implement link type behavior
3. **Schemas**: JSON schemas for validating link configurations
4. **Requirements**: Dependencies needed by the plugin

Example plugin directory structure:
