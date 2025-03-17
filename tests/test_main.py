import json
import sys
import tempfile
from pathlib import Path

import pytest

# Fix import to use the correct path for main.py
from ..main import main

# Create a fake LexiconManager to replace the real one during tests
class FakeLexiconManager:
    def __init__(self, lexicon_dir: str):
        self.lexicon_dir = lexicon_dir
    def get_all_words(self):
        return []  # For testing, pretend there are no words.
    def search(self, criteria):
        # Return a dummy list when searching.
        return [{"word_id": "fake-1", "core": {"part_of_speech": criteria.get("part_of_speech", "noun")}}]
    def create_word_from_recipe(self, recipe_output):
        return "fake-recipe-word"
    def update_word(self, word_id, updates):
        # Return a dummy updated word.
        return {"word_id": word_id, "updated": True}
    def migrate_schema(self, target_version):
        return 0

@pytest.fixture
def fake_manager(monkeypatch):
    # Create a factory function that returns our fake manager
    def fake_lexicon_factory(*args, **kwargs):
        return FakeLexiconManager(*args, **kwargs)
        
    # Replace LexiconManager in the globals of main.py so that main() uses our fake
    monkeypatch.setitem(main.__globals__, "LexiconManager", fake_lexicon_factory)

def run_main_with_args(args, monkeypatch, capsys):
    # Set sys.argv to simulate command line input.
    monkeypatch.setattr(sys, "argv", args)
    try:
        main()
    except SystemExit:
        # argparse calls sys.exit(), so we catch this.
        pass
    return capsys.readouterr().out

def test_list_command(monkeypatch, capsys, fake_manager):
    out = run_main_with_args(["main.py", "list"], monkeypatch, capsys)
    assert "Lexicon contains 0 words" in out

def test_search_command(monkeypatch, capsys, fake_manager):
    out = run_main_with_args(["main.py", "search", "--origin_language", "TestLang", "--part_of_speech", "noun"], 
                             monkeypatch, capsys)
    # Expected fake search returns one word.
    assert "Found 1 words" in out

def test_execute_command(monkeypatch, tmp_path, capsys, fake_manager):
    # Create a temporary recipe JSON file.
    recipe = {"dummy": "data"}
    recipe_file = tmp_path / "recipe.json"
    recipe_file.write_text(json.dumps(recipe))
    out = run_main_with_args(["main.py", "execute", "--recipe_file", str(recipe_file)], monkeypatch, capsys)
    assert "Executed recipe, new word ID: fake-recipe-word" in out

def test_update_command(monkeypatch, capsys, fake_manager):
    out = run_main_with_args(["main.py", "update", "fake-word", "--synonyms", "alpha", "beta"], monkeypatch, capsys)
    assert "Updated word fake-word" in out

def test_migrate_command(monkeypatch, capsys, fake_manager):
    out = run_main_with_args(["main.py", "migrate", "1.1"], monkeypatch, capsys)
    assert "Migrated 0 words to schema 1.1" in out
