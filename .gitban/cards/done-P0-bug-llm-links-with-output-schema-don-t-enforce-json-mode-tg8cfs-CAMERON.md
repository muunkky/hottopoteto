# Bug: LLM links with output_schema don't enforce JSON mode

## Problem
When using `type: llm` with `output_schema` defined, the executor doesn't tell OpenAI to return JSON format. The LLM returns free-form reasoning text instead of structured JSON, breaking schema-based extraction.

## Impact
- Eldorian word recipe fails at storage.save (filename contains reasoning text)
- `{{ Apply_Phonology.data.updated_word }}` contains thousands of chars of LLM reasoning
- storage.update references become unusable
- Custom filename generation fails with Invalid Argument errors

## Root Cause
`core/executor.py` line 898: `ChatOpenAI(model_name, temperature, max_tokens).invoke(formatted_prompt)` doesn't pass `response_format={"type": "json_object"}` when `output_schema` is present.

## Expected Behavior
When `output_schema` is defined, automatically set OpenAI's JSON mode to enforce structured output.

## Actual Behavior
LLM returns natural language reasoning, executor tries `extract_json()` fallback but fails silently.

## Fix
Add `response_format` parameter to ChatOpenAI when `output_schema` exists:

```python
# Line ~898 in core/executor.py
if output_schema:
    llm = ChatOpenAI(
        model_name=model_name, 
        temperature=temperature, 
        max_tokens=token_limit,
        response_format={"type": "json_object"}  # ADD THIS
    )
    # Also prepend to prompt: "Return valid JSON matching this schema:"
else:
    llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=token_limit)
```

## Test Cases
1. Run eldorian_word_v2 recipe - should complete with structured output
2. Check `{{ Apply_Phonology.data.updated_word }}` contains just the word, not reasoning
3. Verify storage.save succeeds with clean filename
4. Test with simple output_schema (one field)
5. Test with complex output_schema (nested objects/arrays)

## Alternative Solution
Change all recipe links to use `llm.extract_to_schema` instead of `llm` with `output_schema`. But this is a framework bug - output_schema should "just work".

## Test Run 1 - JSON Mode Fix

## Test Results - OpenAI JSON Mode Requirement

**Error encountered:**
```
'messages' must contain the word 'json' in some form, to use 'response_format' of type 'json_object'.
```

**Root cause:** OpenAI API requires the word "json" appear in the prompt when using `response_format={"type": "json_object"}`. This is a safety measure.

**Fix applied:**
Added prompt prepending when `output_schema` is present:
```python
if output_schema:
    formatted_prompt = "Return valid JSON matching the schema.\n\n" + formatted_prompt
```

**Location:** `core/executor.py` line ~868 (before conversation_mode check)

**Status:** Fix applied, ready for re-test

## Resolution

**Fix Verified in Codebase (2026-01-14):**

Code inspection confirms both fixes are in place:

1. **Prompt prepending** - Line 1073:
   ```python
   formatted_prompt = "Return valid JSON matching the schema.\n\n" + formatted_prompt
   ```

2. **JSON mode response_format** - Lines 1102 & 1177:
   ```python
   model_kwargs["response_format"] = {"type": "json_object"}
   ```

**Status:** Implementation complete. Full end-to-end validation with OpenAI API is tracked in card c2klz1 (Eldorian Word Recipe E2E Validation).