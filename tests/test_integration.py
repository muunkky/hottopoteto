# tests/test_integration.py

import os
import pytest
from utils.config_loader import load_config

# --- Dummy chain implementations for testing --- #
class DummyChain:
    def __init__(self, output):
        self.output = output

    def run(self, inputs):
        return self.output

class DummySequentialChain:
    def __init__(self, chains):
        self.chains = chains

    def run(self, inputs):
        outputs = {}
        for i, chain in enumerate(self.chains):
            output = chain.run(inputs)
            outputs[f"step_{i+1}"] = output
            inputs[f"step_{i+1}_output"] = output
        return outputs

# --- Sample recipe YAML content --- #
SAMPLE_YAML = """
steps:
  - name: "Initial Prompt"
    type: "prompt"
    template: "prompts/initial_prompt.txt"
    parameters:
      user_input: "Enter your query here"
    output_format: "text"
    token_limit: 100

  - name: "Database Query"
    type: "sql"
    query: "prompts/sample_query.sql"
    parameters:
      record_id: "12345"
    output_format: "json"
    db_config: "configs/db_config.yaml"

  - name: "Agent Function Call"
    type: "agent"
    function: "agents/custom_function.py"
    parameters:
      data: "sample data"
    output_format: "text"
    token_limit: 50
"""

# --- Fixtures --- #
@pytest.fixture
def sample_recipe_file(tmp_path):
    file = tmp_path / "sample_recipe.yaml"
    file.write_text(SAMPLE_YAML)
    return str(file)

@pytest.fixture(autouse=True)
def set_env():
    # Set any required environment variables for substitution, if needed.
    os.environ["DUMMY"] = "dummy_value"
    yield
    os.environ.pop("DUMMY", None)

# --- Dummy build functions to replace external dependencies --- #
def dummy_build_prompt_chain(step):
    return DummyChain("prompt_output")

def dummy_build_sql_chain(step):
    return DummyChain("sql_output")

def dummy_build_agent_chain(step):
    return DummyChain("agent_output")

def dummy_build_sequential_chain(chains_list, input_vars):
    return DummySequentialChain(chains_list)

# --- Patch the build functions using monkeypatch --- #
@pytest.fixture(autouse=True)
def patch_build_functions(monkeypatch):
    from chains import prompt_chain, sql_chain, agent_chain, sequential_chain
    monkeypatch.setattr(prompt_chain, "build_prompt_chain", dummy_build_prompt_chain)
    monkeypatch.setattr(sql_chain, "build_sql_chain", dummy_build_sql_chain)
    monkeypatch.setattr(agent_chain, "build_agent_chain", dummy_build_agent_chain)
    monkeypatch.setattr(sequential_chain, "build_sequential_chain", dummy_build_sequential_chain)

# --- Integration test --- #
def test_full_workflow(sample_recipe_file, caplog):
    # Load recipe configuration from temporary file
    recipe = load_config(sample_recipe_file)
    steps = recipe.steps

    chains_list = []
    input_variables = {"user_input": "test input"}
    
    # Build chain objects based on the recipe steps
    for step in steps:
        if step.type == "prompt":
            from chains.prompt_chain import build_prompt_chain
            chain = build_prompt_chain(step.dict())
        elif step.type == "sql":
            from chains.sql_chain import build_sql_chain
            chain = build_sql_chain(step.dict())
        elif step.type == "agent":
            from chains.agent_chain import build_agent_chain
            chain = build_agent_chain(step.dict())
        else:
            raise ValueError(f"Unsupported step type: {step.type}")
        chains_list.append(chain)
    
    # Build the sequential chain using the patched dummy sequential chain
    from chains.sequential_chain import build_sequential_chain
    sequential_chain = build_sequential_chain(chains_list, list(input_variables.keys()))
    
    # Run the sequential chain
    result = sequential_chain.run(input_variables)
    
    # Assert that the outputs from each step are as expected
    expected_result = {
        "step_1": "prompt_output",
        "step_2": "sql_output",
        "step_3": "agent_output"
    }
    assert result == expected_result

    # Check that logging captured expected messages (e.g., successful configuration loading)
    assert "Successfully loaded configuration file:" in caplog.text
