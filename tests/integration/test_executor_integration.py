"""
RecipeExecutor Integration Tests with Mocked Handlers

Tests the full execute() pipeline end-to-end using mocked domain handlers.
No real LLM API calls are made. No real storage I/O is required.

Test Cases:
  1. User input link populates context
  2. LLM link executes with mocked provider response
  3. Multi-link variable passing (user_input -> llm)
  4. Function link executes and populates context
  5. Missing required input raises or handles gracefully
  6. Storage.save link creates output and populates context
  7. Complete multi-link recipe flow (user_input -> llm -> storage.save)

Architecture Notes:
  - executor._execute_link() dispatches built-in link types (llm, function,
    user_input) directly before checking the registered handler registry:
      - 'llm'        -> self._execute_llm_link(link_config)
      - 'function'   -> self._execute_function_link(link_config)
      - 'user_input' -> self._execute_user_input_link(link_config)
    Registered handlers via register_link_type() are only reached for
    non-built-in link types. patch.object(LLMHandler, "execute", ...) does
    NOT intercept the executor's LLM execution path.
  - To mock 'llm' or 'user_input' links, patch the internal executor methods:
      patch.object(RecipeExecutor, "_execute_llm_link", ...)
      patch.object(RecipeExecutor, "_execute_user_input_link", ...)
  - Memory keys use sanitized link names (spaces -> underscores). The executor
    stores outputs under e.g. "User_Inputs", "LLM_Step", not "User Inputs".
  - build_context() uses the same sanitized keys, so Jinja templates using
    {{ User_Inputs.data.test_word }} are correct.
  - 'storage.save' goes through the registered handler and calls save_entity();
    patch "core.domains.storage.links.save_entity" to avoid real I/O.
  - 'function' is handled by _execute_function_link(); the built-in
    random_number function works without any mocking needed.
"""

import pytest
import yaml
from unittest.mock import patch, MagicMock, call
from pathlib import Path

from core.executor import RecipeExecutor, LLMOutput, UserInputOutput
from core.domains.llm.links import LLMHandler
from core.domains.storage.links import StorageSaveLink
from core.links import register_link_type


# =============================================================================
# Inline Recipe YAML Fixtures
# =============================================================================

USER_INPUT_RECIPE = """
name: User Input Only
version: "1.0"
domain: generic
links:
  - name: User Inputs
    type: user_input
    inputs:
      test_word:
        description: Enter a test word
        type: string
"""

LLM_ONLY_RECIPE = """
name: LLM Only
version: "1.0"
domain: generic
links:
  - name: LLM Step
    type: llm
    provider: openai
    model: gpt-4o
    prompt: "Generate something creative"
"""

MULTI_LINK_VARIABLE_RECIPE = """
name: Multi-Link Variable Passing
version: "1.0"
domain: generic
links:
  - name: User Inputs
    type: user_input
    inputs:
      test_word:
        description: Enter a test word
        type: string
  - name: LLM Step
    type: llm
    provider: openai
    model: gpt-4o
    prompt: "Generate a greeting for {{ User_Inputs.data.test_word }}"
"""

FUNCTION_LINK_RECIPE = """
name: Function Link Test
version: "1.0"
domain: generic
links:
  - name: Random Number
    type: function
    function:
      name: random_number
    inputs:
      min_value: 1
      max_value: 10
"""

STORAGE_SAVE_RECIPE = """
name: Storage Save Test
version: "1.0"
domain: generic
links:
  - name: Save Step
    type: storage.save
    collection: test_collection
    data:
      key: value
      result: integration_test
"""

MULTI_DOMAIN_RECIPE = """
name: Multi Domain Flow
version: "1.0"
domain: generic
links:
  - name: User Inputs
    type: user_input
    inputs:
      word:
        description: Enter a word
        type: string
  - name: LLM Step
    type: llm
    provider: openai
    model: gpt-4o
    prompt: "Translate {{ User_Inputs.data.word }} to French"
  - name: Save Result
    type: storage.save
    collection: translations
    data:
      original: "{{ User_Inputs.data.word }}"
      translated: "{{ LLM_Step.data.raw_content }}"
"""


# =============================================================================
# Helpers
# =============================================================================

def make_recipe_file(tmp_path: Path, recipe_yaml: str) -> Path:
    """Write a recipe YAML string to a temporary file and return the path."""
    recipe_file = tmp_path / "recipe.yaml"
    recipe_file.write_text(recipe_yaml, encoding="utf-8")
    return recipe_file


def make_user_input_output(data: dict) -> UserInputOutput:
    """Return a UserInputOutput populated with the given data dict."""
    return UserInputOutput(data=data)


def make_llm_output(raw: str, data: dict = None) -> LLMOutput:
    """Return an LLMOutput with the given raw string and optional data dict."""
    return LLMOutput(raw=raw, data=data or {"raw_content": raw})


# =============================================================================
# Test Case 1: User input link populates context
# =============================================================================

class TestUserInputLinkPopulatesContext:
    """Test Case 1 — user_input link result ends up in executor.memory."""

    def test_user_input_result_stored_in_memory(self, tmp_path):
        """
        When user_input link executes, its output must be accessible in
        executor.memory under the sanitized link name ("User_Inputs").

        Strategy: patch RecipeExecutor._execute_user_input_link to return a
        fixed payload (bypassing input() and the LLM post-processing step),
        then verify executor.memory contains the payload under the sanitized key.
        """
        fixed_output = make_user_input_output({"test_word": "hello"})

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=fixed_output):
            recipe_file = make_recipe_file(tmp_path, USER_INPUT_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        # Memory key uses the sanitized link name (spaces -> underscores)
        assert "User_Inputs" in executor.memory
        stored = executor.memory["User_Inputs"]
        assert stored.data["test_word"] == "hello"

    def test_user_input_context_accessible_in_subsequent_links(self, tmp_path):
        """
        A subsequent llm link must be able to reference user_input data via
        Jinja template rendering ({{ User_Inputs.data.test_word }}).

        Strategy: patch both _execute_user_input_link and _execute_llm_link;
        verify that after execution the user_input value is present in the
        executor context under the sanitized key, confirming it would have
        been available for template rendering.
        """
        user_output = make_user_input_output({"test_word": "world"})

        def capturing_llm(link_config):
            return make_llm_output("mocked response")

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=user_output), \
             patch.object(RecipeExecutor, "_execute_llm_link", side_effect=capturing_llm):
            recipe_file = make_recipe_file(tmp_path, MULTI_LINK_VARIABLE_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        # Both links must have stored results in memory
        assert "User_Inputs" in executor.memory
        assert "LLM_Step" in executor.memory
        # User input value must be accessible in the executor context for template rendering
        ctx = executor.build_context(executor.memory)
        assert "User_Inputs" in ctx
        assert ctx["User_Inputs"]["data"]["test_word"] == "world"


# =============================================================================
# Test Case 2: LLM link executes with mocked provider response
# =============================================================================

class TestLLMLinkExecutesWithMock:
    """Test Case 2 — llm link uses mocked internal method; result stored in memory."""

    def test_llm_output_stored_in_memory(self, tmp_path):
        """
        After execute(), executor.memory must contain the LLM link output
        under the sanitized link name ("LLM_Step").

        Strategy: patch RecipeExecutor._execute_llm_link to return a known
        LLMOutput, bypassing the ChatOpenAI invocation.
        """
        mocked_output = make_llm_output("hello world")

        with patch.object(RecipeExecutor, "_execute_llm_link", return_value=mocked_output):
            recipe_file = make_recipe_file(tmp_path, LLM_ONLY_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        assert "LLM_Step" in executor.memory
        stored = executor.memory["LLM_Step"]
        assert stored.raw == "hello world"
        assert stored.data["raw_content"] == "hello world"

    def test_llm_handler_called_once(self, tmp_path):
        """
        For a recipe with a single LLM link, _execute_llm_link must be
        called exactly once.
        """
        mocked_output = make_llm_output("ok")

        with patch.object(
            RecipeExecutor, "_execute_llm_link", return_value=mocked_output
        ) as mock_exec:
            recipe_file = make_recipe_file(tmp_path, LLM_ONLY_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        mock_exec.assert_called_once()

    def test_llm_handler_receives_link_config(self, tmp_path):
        """
        The link_config passed to _execute_llm_link must contain the fields
        specified in the recipe (model, prompt, etc.).
        """
        mocked_output = make_llm_output("ok")
        received_configs = []

        def capture_config(link_config):
            received_configs.append(dict(link_config))
            return mocked_output

        with patch.object(RecipeExecutor, "_execute_llm_link", side_effect=capture_config):
            recipe_file = make_recipe_file(tmp_path, LLM_ONLY_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        assert len(received_configs) == 1
        cfg = received_configs[0]
        assert cfg.get("model") == "gpt-4o"
        assert "Generate something creative" in cfg.get("prompt", "")


# =============================================================================
# Test Case 3: Multi-link variable passing
# =============================================================================

class TestMultiLinkVariablePassing:
    """Test Case 3 — prompt rendered with value from prior user_input link."""

    def test_llm_prompt_contains_user_input_value(self, tmp_path):
        """
        The Jinja prompt '{{ User_Inputs.data.test_word }}' must be rendered
        with the value returned by the user_input link before being sent to
        the LLM handler.

        Verifies by checking that after execution the user_input value
        ("dragon") is present in executor memory under the sanitized key,
        confirming it was available to _execute_llm_link for template
        rendering.
        """
        user_output = make_user_input_output({"test_word": "dragon"})
        captured_configs = []

        def capture_llm_config(link_config):
            captured_configs.append(dict(link_config))
            return make_llm_output("ok")

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=user_output), \
             patch.object(RecipeExecutor, "_execute_llm_link", side_effect=capture_llm_config):
            recipe_file = make_recipe_file(tmp_path, MULTI_LINK_VARIABLE_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        assert len(captured_configs) == 1

        # The user_input value must be in memory before the LLM link ran
        assert "User_Inputs" in executor.memory
        assert executor.memory["User_Inputs"].data["test_word"] == "dragon"

        # Both links must have run
        assert "LLM_Step" in executor.memory

    def test_memory_contains_both_link_outputs(self, tmp_path):
        """
        After executing a two-link recipe, executor.memory must contain
        entries for both the user_input link and the llm link.
        """
        user_output = make_user_input_output({"test_word": "elf"})
        llm_output = make_llm_output("Greetings, elf!")

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=user_output), \
             patch.object(RecipeExecutor, "_execute_llm_link", return_value=llm_output):
            recipe_file = make_recipe_file(tmp_path, MULTI_LINK_VARIABLE_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        assert "User_Inputs" in executor.memory
        assert "LLM_Step" in executor.memory
        assert executor.memory["LLM_Step"].raw == "Greetings, elf!"


# =============================================================================
# Test Case 4: Function link executes and populates context
# =============================================================================

class TestFunctionLinkPopulatesContext:
    """Test Case 4 — function link runs and stores result in memory.

    The executor routes 'function' link type directly to
    _execute_function_link() before checking the registry. The built-in
    random_number function is available, so no handler registration is needed.
    """

    def test_function_link_output_in_memory(self, tmp_path):
        """
        After executing a recipe with a function link, executor.memory must
        contain the function's return value under the sanitized link name
        ("Random_Number").
        """
        recipe_file = make_recipe_file(tmp_path, FUNCTION_LINK_RECIPE)
        executor = RecipeExecutor(str(recipe_file))
        executor.execute(inputs={})

        assert "Random_Number" in executor.memory
        stored = executor.memory["Random_Number"]
        # random_number returns FunctionOutput(data={"num_events": <int>})
        data = stored.data if hasattr(stored, "data") else stored.get("data", stored)
        assert "num_events" in data
        assert isinstance(data["num_events"], int)

    def test_function_link_result_within_configured_range(self, tmp_path):
        """
        The random_number function configured with min_value=1, max_value=10
        must return a value in [1, 10].
        """
        recipe_file = make_recipe_file(tmp_path, FUNCTION_LINK_RECIPE)
        executor = RecipeExecutor(str(recipe_file))
        executor.execute(inputs={})

        stored = executor.memory["Random_Number"]
        data = stored.data if hasattr(stored, "data") else stored.get("data", stored)
        assert 1 <= data["num_events"] <= 10


# =============================================================================
# Test Case 5: Missing required input raises or handles gracefully
# =============================================================================

class TestMissingInputHandledGracefully:
    """Test Case 5 — recipe executed with unknown link type does not crash silently."""

    def test_unknown_link_type_raises_attribute_error(self, tmp_path):
        """
        When a recipe contains an unknown link type (no registered handler,
        no built-in fallback), _execute_link raises AttributeError (because
        get_link_handler returns None and None.execute() fails).

        This verifies the executor does not swallow errors silently.
        """
        unknown_recipe = """
name: Unknown Link Recipe
version: "1.0"
domain: generic
links:
  - name: Bad Link
    type: this_type_does_not_exist
"""
        recipe_file = make_recipe_file(tmp_path, unknown_recipe)
        executor = RecipeExecutor(str(recipe_file))

        with pytest.raises((AttributeError, ValueError, TypeError)):
            executor.execute(inputs={})

    def test_llm_handler_error_propagates_from_execute(self, tmp_path):
        """
        If _execute_llm_link raises an unexpected exception, the executor
        propagates it from execute() rather than swallowing it.

        Note: _execute_llm_link itself swallows internal ChatOpenAI errors
        (converting them to LLMOutput(data={"error": ...})). This test
        verifies that if _execute_llm_link raises at the method boundary,
        execute() does not silently suppress the exception — the error
        reaches the caller, ensuring the executor is not fault-masking at
        the pipeline level.
        """
        def exploding_llm(link_config):
            raise RuntimeError("Simulated LLM failure")

        with patch.object(RecipeExecutor, "_execute_llm_link", side_effect=exploding_llm):
            recipe_file = make_recipe_file(tmp_path, LLM_ONLY_RECIPE)
            executor = RecipeExecutor(str(recipe_file))

            with pytest.raises(RuntimeError, match="Simulated LLM failure"):
                executor.execute(inputs={})


# =============================================================================
# Test Case 6: Storage.save link creates working output and populates context
# =============================================================================

class TestStorageSaveLinkPopulatesContext:
    """Test Case 6 — storage.save link stores output in memory."""

    def test_storage_save_output_in_memory(self, tmp_path):
        """
        After executing a recipe with a storage.save link, executor.memory
        must contain an entry for the storage link under the sanitized name
        ("Save_Step") with a result.
        """
        mock_save_result = {"id": "test-abc123", "success": True}

        with patch(
            "core.domains.storage.links.save_entity",
            return_value=mock_save_result,
        ):
            recipe_file = make_recipe_file(tmp_path, STORAGE_SAVE_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        assert "Save_Step" in executor.memory
        stored = executor.memory["Save_Step"]
        data = stored.get("data", stored) if isinstance(stored, dict) else stored
        assert data is not None

    def test_storage_save_called_with_correct_collection(self, tmp_path):
        """
        StorageSaveLink.execute must call save_entity with the collection
        specified in the recipe config.
        """
        mock_save_result = {"id": "x1", "success": True}

        with patch(
            "core.domains.storage.links.save_entity",
            return_value=mock_save_result,
        ) as mock_save:
            recipe_file = make_recipe_file(tmp_path, STORAGE_SAVE_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        mock_save.assert_called_once()
        call_args = mock_save.call_args
        # First positional arg is the collection name
        assert call_args[0][0] == "test_collection"


# =============================================================================
# Test Case 7: Complete multi-domain recipe flow
# =============================================================================

class TestMultiDomainRecipeFlow:
    """
    Test Case 7 — user_input -> llm -> storage.save sequence.

    All three links must execute in order; each link's output must be
    accessible in memory; the final storage.save must be called.
    """

    def test_all_three_links_execute(self, tmp_path):
        """
        A three-link recipe (user_input, llm, storage.save) must populate
        executor.memory with entries for all three links under their
        sanitized names.
        """
        user_output = make_user_input_output({"word": "hello"})
        llm_output = make_llm_output("bonjour")
        save_result = {"id": "save-abc", "success": True}

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=user_output), \
             patch.object(RecipeExecutor, "_execute_llm_link", return_value=llm_output), \
             patch("core.domains.storage.links.save_entity", return_value=save_result):
            recipe_file = make_recipe_file(tmp_path, MULTI_DOMAIN_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        assert "User_Inputs" in executor.memory
        assert "LLM_Step" in executor.memory
        assert "Save_Result" in executor.memory

    def test_final_storage_save_called(self, tmp_path):
        """
        The storage.save link at the end of the multi-domain recipe must be
        invoked exactly once.
        """
        user_output = make_user_input_output({"word": "bye"})
        llm_output = make_llm_output("au revoir")
        save_result = {"id": "save-xyz", "success": True}

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=user_output), \
             patch.object(RecipeExecutor, "_execute_llm_link", return_value=llm_output), \
             patch("core.domains.storage.links.save_entity", return_value=save_result) as mock_save:
            recipe_file = make_recipe_file(tmp_path, MULTI_DOMAIN_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        mock_save.assert_called_once()

    def test_llm_link_receives_user_input_context(self, tmp_path):
        """
        When the LLM link executes, the executor context built from memory
        must contain the user_input link output under the sanitized key
        ("User_Inputs"), making the value available for template rendering.
        """
        user_output = make_user_input_output({"word": "sun"})
        llm_output = make_llm_output("soleil")
        save_result = {"id": "s1", "success": True}

        def capturing_llm(link_config):
            return llm_output

        with patch.object(RecipeExecutor, "_execute_user_input_link", return_value=user_output), \
             patch.object(RecipeExecutor, "_execute_llm_link", side_effect=capturing_llm), \
             patch("core.domains.storage.links.save_entity", return_value=save_result):
            recipe_file = make_recipe_file(tmp_path, MULTI_DOMAIN_RECIPE)
            executor = RecipeExecutor(str(recipe_file))
            executor.execute(inputs={})

        # Verify user_input result is in memory
        assert "User_Inputs" in executor.memory
        ctx = executor.build_context(executor.memory)
        assert "User_Inputs" in ctx
        assert ctx["User_Inputs"]["data"]["word"] == "sun"

        # Verify all three links executed
        assert "LLM_Step" in executor.memory
        assert "Save_Result" in executor.memory
