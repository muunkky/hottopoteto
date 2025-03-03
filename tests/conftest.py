# tests/conftest.py
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before running tests"""
    load_dotenv()
    assert os.getenv("OPENAI_API_KEY"), "❌ OPENAI_API_KEY is missing"
    print("✅ OPENAI_API_KEY loaded successfully")
