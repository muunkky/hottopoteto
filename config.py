import os
from dotenv import load_dotenv

print("Loading .env file...")  # Debugging statement
load_dotenv()  # Load environment variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/data.db")

print(f"OPENAI_API_KEY from os.environ: {OPENAI_API_KEY}")  # Debugging statement

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY environment variable is not set")