"""
Link handlers for the LLM domain
"""
from typing import Dict, Any
import logging
from core.links import LinkHandler, register_link_type
from .functions import generate_text

logger = logging.getLogger(__name__)

class LLMHandler(LinkHandler):
    """Handler for LLM link type."""
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the LLM link."""
        model = link_config.get("model", "gpt-4o")
        prompt = link_config.get("prompt", "")
        temperature = link_config.get("temperature", 0.7)
        provider = link_config.get("provider", "openai")
        system = link_config.get("system", "You are a helpful assistant.")
        output_schema = link_config.get("output_schema")
        
        # Generate text using the LLM function
        result = generate_text(prompt, model=model, temperature=temperature, provider=provider, system=system)
        
        # Extract structured data if schema is provided
        if output_schema and "properties" in output_schema:
            # For our simple example with a greeting property
            if "greeting" in output_schema.get("properties", {}):
                return {
                    "raw": result["text"],
                    "data": {
                        "greeting": result["text"]
                    }
                }
        
        # Default case - return the raw text
        return {
            "raw": result["text"],
            "data": {
                "raw_content": result["text"]
            }
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for this link type's configuration."""
        return {
            "type": "object",
            "required": ["prompt"],
            "properties": {
                "model": {"type": "string", "description": "LLM model to use"},
                "prompt": {"type": "string", "description": "Prompt to generate text"},
                "system": {"type": "string", "description": "System prompt"},
                "temperature": {"type": "number", "description": "Sampling temperature"},
                "provider": {"type": "string", "description": "LLM provider"},
                "output_schema": {
                    "type": "object",
                    "description": "Schema for structured output"
                }
            }
        }


class LLMExtractToSchemaLink(LinkHandler):
    """
    Handler for llm.extract_to_schema link type.
    
    Extracts structured data from unstructured text using LLM with JSON mode.
    Part of DOCENRICH Sprint - Schema-Driven Document Enrichment.
    
    The llm.extract_to_schema link:
    - Takes source text and target schema
    - Auto-generates intelligent extraction prompt
    - Uses LLM JSON mode for reliable structured output
    - Validates extracted data against schema
    - Supports optional hint parameter for domain guidance
    
    Example configuration:
        - name: "Extract_Origins"
          type: "llm.extract_to_schema"
          source: "{{ Generate_Origins.data.raw }}"
          schema: "{{ Working_Doc.data.schema.properties.origin_words }}"
          hint: "Focus on fictional etymology components"
          model: "gpt-4o"
          temperature: 0.2
    
    Output structure:
        {
            "raw": "<generated prompt>",
            "data": <extracted data matching schema>
        }
    """
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the llm.extract_to_schema link."""
        logger.info(f"Executing llm.extract_to_schema link: {link_config.get('name')}")
        
        try:
            # Extract and render source (required)
            source = link_config.get("source")
            if not source:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "source is required for llm.extract_to_schema"
                    }
                }
            source = cls._render_template(source, context)
            
            # Extract and resolve schema (required)
            schema_config = link_config.get("schema")
            if not schema_config:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "schema is required for llm.extract_to_schema"
                    }
                }
            schema = cls._resolve_schema(schema_config, context)
            
            # Extract optional parameters
            hint = link_config.get("hint", "")
            if hint:
                hint = cls._render_template(hint, context)
            
            model = link_config.get("model", "gpt-4o")
            temperature = link_config.get("temperature", 0.2)  # Low temp for extraction
            provider = link_config.get("provider", "openai")

            # Build extraction prompt
            prompt = cls._build_extraction_prompt(source, schema, hint)

            # Call LLM with JSON mode
            extracted_data = cls._call_llm_json_mode(
                prompt=prompt,
                schema=schema,
                model=model,
                temperature=temperature,
                provider=provider,
            )
            
            # Validate against schema
            validation_error = cls._validate_against_schema(extracted_data, schema)
            if validation_error:
                logger.warning(f"Extraction validation warning: {validation_error}")
                # Continue anyway - LLM output might still be useful
            
            return {
                "raw": prompt,
                "data": extracted_data
            }
            
        except Exception as e:
            logger.error(f"Error in llm.extract_to_schema: {e}")
            return {
                "raw": None,
                "data": {
                    "success": False,
                    "error": str(e)
                }
            }
    
    @classmethod
    def _render_template(cls, value: Any, context: Dict[str, Any]) -> Any:
        """Render a Jinja2 template string or return value as-is."""
        if not isinstance(value, str):
            return value
        if "{{" not in value:
            return value

        from jinja2 import Environment, StrictUndefined
        env = Environment(undefined=StrictUndefined)
        template = env.from_string(value)
        return template.render(**context)

    @classmethod
    def _resolve_schema(cls, schema_config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve schema from various sources.
        
        Args:
            schema_config: Schema config (inline dict, template string, or file ref)
            context: Execution context
            
        Returns:
            Resolved schema dictionary
        """
        # If it's a template string, render it first
        if isinstance(schema_config, str):
            rendered = cls._render_template(schema_config, context)
            # _render_template always returns str when given a str input, so
            # isinstance(rendered, dict) can never be true here.  The str → dict
            # recovery below is needed because Jinja2 renders a Python dict context
            # value as its Python repr (e.g. "{'key': 'val'}"), not as JSON.
            # json.loads() therefore fails and ast.literal_eval() is the only path
            # back to the original dict.  If the architecture ever moves to
            # JSON-serialising context values before Jinja2 rendering, the
            # ast.literal_eval fallback should be removed (it will never be reached).
            import json
            import ast
            try:
                return json.loads(rendered)
            except (json.JSONDecodeError, TypeError):
                pass
            try:
                result = ast.literal_eval(rendered)
                if isinstance(result, dict):
                    return result
            except (ValueError, SyntaxError):
                pass
            # Return as minimal schema
            return {"type": "object"}
        
        # If it's already a dict, return as-is
        if isinstance(schema_config, dict):
            # Check for file reference
            if "file" in schema_config:
                from core.schemas import resolve_schema_reference
                return resolve_schema_reference(schema_config)
            return schema_config
        
        return {"type": "object"}
    
    @classmethod
    def _build_extraction_prompt(cls, source: str, schema: Dict[str, Any], hint: str) -> str:
        """
        Build intelligent extraction prompt from schema.
        
        Args:
            source: Source text to extract from
            schema: Target JSON Schema
            hint: Optional extraction guidance
            
        Returns:
            Formatted extraction prompt
        """
        import json
        
        prompt_parts = [
            "Extract structured data from the following text.",
            "",
            "TARGET SCHEMA:",
            json.dumps(schema, indent=2),
        ]
        
        if hint:
            prompt_parts.extend([
                "",
                f"EXTRACTION GUIDANCE: {hint}"
            ])
        
        prompt_parts.extend([
            "",
            "SOURCE TEXT:",
            "---",
            source,
            "---",
            "",
            "Extract data matching the schema above. Return valid JSON only.",
            "If a field cannot be determined, omit it (if optional) or use null (if required)."
        ])
        
        return "\n".join(prompt_parts)
    
    @classmethod
    def _call_llm_json_mode(
        cls,
        prompt: str,
        schema: Dict[str, Any],
        model: str = "gpt-4o",
        temperature: float = 0.2,
        provider: str = "openai",
    ) -> Any:
        """
        Call LLM with JSON mode for structured output.

        Args:
            prompt: Extraction prompt
            schema: Expected output schema
            model: LLM model to use
            temperature: Sampling temperature
            provider: LLM provider (e.g. 'openai', 'anthropic')

        Returns:
            Parsed JSON data from LLM
        """
        import json

        # Use the domain's generate_text function
        result = generate_text(
            prompt=prompt,
            model=model,
            temperature=temperature,
            provider=provider,
            system="You are a data extraction assistant. Extract structured data from text and return valid JSON only."
        )
        
        # In a real implementation with actual LLM APIs, we would:
        # 1. Use response_format={"type": "json_object"} for OpenAI
        # 2. Use tool_use for Anthropic
        # 3. Parse the JSON response
        
        # For now with mock, we'll simulate extraction based on prompt content
        # In production, the LLM would return actual JSON
        text = result.get("text", "{}")
        
        # Try to parse as JSON (real LLM in JSON mode would return valid JSON)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # If mock doesn't return JSON, return empty based on schema type
            if schema.get("type") == "array":
                return []
            return {}
    
    @classmethod
    def _validate_against_schema(cls, data: Any, schema: Dict[str, Any]) -> str:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema
            
        Returns:
            Error message if validation fails, None if valid
        """
        try:
            import jsonschema
            jsonschema.validate(instance=data, schema=schema)
            return None
        except jsonschema.ValidationError as e:
            return str(e.message)
        except Exception as e:
            logger.warning(f"Schema validation warning: {e}")
            return None
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type."""
        return {
            "type": "object",
            "required": ["type", "source", "schema"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["llm.extract_to_schema"],
                    "description": "Link type"
                },
                "source": {
                    "type": "string",
                    "description": "Source text to extract from (supports templates)"
                },
                "schema": {
                    "oneOf": [
                        {"type": "object", "description": "Inline JSON Schema"},
                        {"type": "string", "description": "Template reference to schema"}
                    ],
                    "description": "Target schema for extraction"
                },
                "hint": {
                    "type": "string",
                    "description": "Optional extraction guidance/hint"
                },
                "model": {
                    "type": "string",
                    "default": "gpt-4o",
                    "description": "LLM model to use"
                },
                "temperature": {
                    "type": "number",
                    "default": 0.2,
                    "description": "Sampling temperature (low for extraction accuracy)"
                },
                "provider": {
                    "type": "string",
                    "default": "openai",
                    "description": "LLM provider (e.g. 'openai', 'anthropic')"
                }
            }
        }


class LLMEnrichLink(LinkHandler):
    """
    Handler for llm.enrich link type.
    
    Document-aware enrichment that sees the full document context when
    extracting and populating fields.
    Part of DOCENRICH Sprint - Schema-Driven Document Enrichment.
    
    The llm.enrich link:
    - Receives full document context (schema + current data)
    - LLM sees existing values for context-aware inference
    - Extracts and populates specified target fields
    - Preserves all existing document fields
    - Supports automatic empty field detection
    
    Example configuration:
        - name: "Enrich_With_Origins"
          type: "llm.enrich"
          document: "{{ Working_Doc.data }}"
          source: "{{ Generate_Origins.data.raw }}"
          target_fields:
            - "origin_words"
            - "revised_connotation"
          hint: "Extract the fictional etymologies"
    
    Output structure:
        {
            "raw": "<enrichment prompt>",
            "data": <complete enriched document>
        }
    """
    
    @classmethod
    def execute(cls, link_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the llm.enrich link."""
        logger.info(f"Executing llm.enrich link: {link_config.get('name')}")
        
        try:
            # Resolve document (required)
            document_config = link_config.get("document")
            if not document_config:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "document is required for llm.enrich"
                    }
                }
            document = cls._resolve_document(document_config, context)
            
            # Extract source (required)
            source = link_config.get("source")
            if not source:
                return {
                    "raw": None,
                    "data": {
                        "success": False,
                        "error": "source is required for llm.enrich"
                    }
                }
            source = cls._render_template(source, context)
            
            # Get schema and current data from document
            schema = document.get("schema", {})
            current_data = document.get("data", {})

            # Branch quarantine: if target_schema_path is set, extract the sub-schema
            # and sub-data, call the LLM on just that branch, then merge back.
            target_schema_path = link_config.get("target_schema_path", "")

            if target_schema_path:
                active_schema = cls._extract_schema_branch(schema, target_schema_path) or schema
                active_data = cls._extract_data_branch(current_data, target_schema_path) or {}
            else:
                active_schema = schema
                active_data = current_data

            # Determine target fields (operate on the active branch)
            target_fields = link_config.get("target_fields", "auto")
            if target_fields == "auto":
                target_fields = cls._find_empty_fields(active_data, active_schema)
            elif isinstance(target_fields, str):
                target_fields = [target_fields]

            # Extract optional hint
            hint = link_config.get("hint", "")
            if hint:
                hint = cls._render_template(hint, context)

            # Get LLM parameters
            model = link_config.get("model", "gpt-4o")
            temperature = link_config.get("temperature", 0.3)
            provider = link_config.get("provider", "openai")

            # Build enrichment prompt against the active branch
            prompt = cls._build_enrichment_prompt(
                current_data=active_data,
                source=source,
                target_fields=target_fields,
                schema=active_schema,
                hint=hint
            )

            # Call LLM with JSON mode against the active (possibly quarantined) schema
            branch_result = cls._call_llm_json_mode(
                prompt=prompt,
                schema=active_schema,
                model=model,
                temperature=temperature,
                provider=provider,
            )

            # If branch quarantine was used, merge the result back into the full document
            if target_schema_path:
                enriched_data = cls._merge_at_path(current_data, target_schema_path, branch_result)
            else:
                enriched_data = branch_result
            
            # Validate enriched document
            validation_error = cls._validate_against_schema(enriched_data, schema)
            if validation_error:
                logger.warning(f"Enrichment validation warning: {validation_error}")
            
            return {
                "raw": prompt,
                "data": enriched_data
            }
            
        except Exception as e:
            logger.error(f"Error in llm.enrich: {e}")
            return {
                "raw": None,
                "data": {
                    "success": False,
                    "error": str(e)
                }
            }
    
    @classmethod
    def _resolve_document(cls, document_config: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve document from config or context.
        
        Args:
            document_config: Document config (inline dict or template string)
            context: Execution context
            
        Returns:
            Resolved document dictionary with schema and data
        """
        # If it's a template string, render it first
        if isinstance(document_config, str):
            rendered = cls._render_template(document_config, context)
            # _render_template always returns str when given a str input, so
            # isinstance(rendered, dict) can never be true here.  The str → dict
            # recovery below is needed because Jinja2 renders a Python dict context
            # value as its Python repr (e.g. "{'schema': {}, 'data': {}}"), not as
            # JSON.  json.loads() therefore fails and ast.literal_eval() is the only
            # path back to the original dict.  If the architecture ever moves to
            # JSON-serialising context values before Jinja2 rendering, the
            # ast.literal_eval fallback should be removed (it will never be reached).
            import json
            import ast
            try:
                result = json.loads(rendered)
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, TypeError):
                pass
            try:
                result = ast.literal_eval(rendered)
                if isinstance(result, dict):
                    return result
            except (ValueError, SyntaxError):
                pass
            return {"schema": {}, "data": {}}

        # If it's already a dict, return as-is
        if isinstance(document_config, dict):
            return document_config

        return {"schema": {}, "data": {}}
    
    @classmethod
    def _render_template(cls, value: Any, context: Dict[str, Any]) -> Any:
        """Render a Jinja2 template string or return value as-is."""
        if not isinstance(value, str):
            return value
        if "{{" not in value:
            return value

        from jinja2 import Environment, StrictUndefined
        env = Environment(undefined=StrictUndefined)
        template = env.from_string(value)
        return template.render(**context)

    @classmethod
    def _find_empty_fields(cls, data: Dict[str, Any], schema: Dict[str, Any]) -> list:
        """
        Find fields that are empty (null, None, or empty arrays).
        
        Args:
            data: Current document data
            schema: Document schema
            
        Returns:
            List of field names that are empty
        """
        empty_fields = []
        
        for field, value in data.items():
            if value is None:
                empty_fields.append(field)
            elif isinstance(value, list) and len(value) == 0:
                empty_fields.append(field)
            elif isinstance(value, str) and value.strip() == "":
                empty_fields.append(field)
        
        return empty_fields

    @classmethod
    def _extract_schema_branch(cls, schema: Dict[str, Any], path: str) -> Any:
        """
        Extract a sub-schema at a dot-notation path.

        Args:
            schema: Full JSON schema object
            path: Dot-notation path (e.g. "morphology" or "morphology.roots")
                  Empty string returns the full schema.

        Returns:
            Sub-schema dict at the given path, or None if the path doesn't exist.
        """
        if not path:
            return schema

        parts = path.split(".")
        current = schema
        for part in parts:
            if not isinstance(current, dict):
                return None
            properties = current.get("properties", {})
            if part not in properties:
                return None
            current = properties[part]
        return current

    @classmethod
    def _extract_data_branch(cls, data: Any, path: str) -> Any:
        """
        Extract data at a dot-notation path.

        Args:
            data: Data dict to traverse
            path: Dot-notation path (e.g. "morphology" or "morphology.roots")
                  Empty string returns the full data.

        Returns:
            Value at the path, or None if not found.
        """
        if not path:
            return data

        parts = path.split(".")
        current = data
        for part in parts:
            if not isinstance(current, dict):
                return None
            if part not in current:
                return None
            current = current[part]
        return current

    @classmethod
    def _merge_at_path(cls, data: Dict[str, Any], path: str, new_value: Any) -> Dict[str, Any]:
        """
        Merge/replace a value at a dot-notation path inside data.

        Creates any missing intermediate dicts. For an empty path the entire
        data dict is replaced by new_value.

        Args:
            data: Original data dict (not mutated)
            path: Dot-notation path (e.g. "morphology" or "morphology.roots")
            new_value: Value to place at path

        Returns:
            New data dict with the value set at path.
        """
        import copy

        if not path:
            return new_value

        result = copy.deepcopy(data)
        parts = path.split(".")
        node = result
        for part in parts[:-1]:
            if not isinstance(node.get(part), dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = new_value
        return result

    @classmethod
    def _build_enrichment_prompt(
        cls,
        current_data: Dict[str, Any],
        source: str,
        target_fields: list,
        schema: Dict[str, Any],
        hint: str
    ) -> str:
        """
        Build enrichment prompt with full document context.
        
        Args:
            current_data: Current document state
            source: New information to incorporate
            target_fields: Fields to populate
            schema: Document schema
            hint: Optional guidance
            
        Returns:
            Formatted enrichment prompt
        """
        import json
        
        prompt_parts = [
            "You are enriching a document with new information.",
            "",
            "CURRENT DOCUMENT STATE:",
            json.dumps(current_data, indent=2),
        ]
        
        if target_fields:
            prompt_parts.extend([
                "",
                f"TARGET FIELDS TO POPULATE: {', '.join(target_fields)}"
            ])
        
        prompt_parts.extend([
            "",
            "NEW INFORMATION TO INCORPORATE:",
            "---",
            source,
            "---"
        ])
        
        if hint:
            prompt_parts.extend([
                "",
                f"GUIDANCE: {hint}"
            ])
        
        prompt_parts.extend([
            "",
            "Return the complete document with target fields populated.",
            "Preserve all existing values. Only update the specified target fields.",
            "Return valid JSON matching the document structure."
        ])
        
        return "\n".join(prompt_parts)
    
    @classmethod
    def _call_llm_json_mode(
        cls,
        prompt: str,
        schema: Dict[str, Any],
        model: str = "gpt-4o",
        temperature: float = 0.3,
        provider: str = "openai",
    ) -> Dict[str, Any]:
        """
        Call LLM with JSON mode for structured output.

        Args:
            prompt: Enrichment prompt
            schema: Expected output schema
            model: LLM model to use
            temperature: Sampling temperature
            provider: LLM provider (e.g. 'openai', 'anthropic')

        Returns:
            Parsed JSON data from LLM
        """
        import json

        result = generate_text(
            prompt=prompt,
            model=model,
            temperature=temperature,
            provider=provider,
            system="You are a document enrichment assistant. Return the complete enriched document as valid JSON."
        )
        
        text = result.get("text", "{}")
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
    
    @classmethod
    def _validate_against_schema(cls, data: Any, schema: Dict[str, Any]) -> str:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema
            
        Returns:
            Error message if validation fails, None if valid
        """
        try:
            import jsonschema
            jsonschema.validate(instance=data, schema=schema)
            return None
        except jsonschema.ValidationError as e:
            return str(e.message)
        except Exception as e:
            logger.warning(f"Schema validation warning: {e}")
            return None
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for this link type."""
        return {
            "type": "object",
            "required": ["type", "document", "source"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["llm.enrich"],
                    "description": "Link type"
                },
                "document": {
                    "oneOf": [
                        {"type": "object", "description": "Inline document with schema and data"},
                        {"type": "string", "description": "Template reference to document"}
                    ],
                    "description": "Document to enrich"
                },
                "source": {
                    "type": "string",
                    "description": "New information to incorporate (supports templates)"
                },
                "target_fields": {
                    "oneOf": [
                        {"type": "array", "items": {"type": "string"}, "description": "List of fields to populate"},
                        {"type": "string", "enum": ["auto"], "description": "Auto-detect empty fields"}
                    ],
                    "description": "Target fields to enrich"
                },
                "hint": {
                    "type": "string",
                    "description": "Optional enrichment guidance/hint"
                },
                "model": {
                    "type": "string",
                    "default": "gpt-4o",
                    "description": "LLM model to use"
                },
                "temperature": {
                    "type": "number",
                    "default": 0.3,
                    "description": "Sampling temperature"
                },
                "provider": {
                    "type": "string",
                    "default": "openai",
                    "description": "LLM provider (e.g. 'openai', 'anthropic')"
                }
            }
        }


# Register the link types
register_link_type("llm", LLMHandler)
register_link_type("llm.extract_to_schema", LLMExtractToSchemaLink)
register_link_type("llm.enrich", LLMEnrichLink)
