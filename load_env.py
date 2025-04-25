from pathlib import Path
from dotenv import load_dotenv
import os

def load_environment():
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    print("Environment variables loaded from .env")

if __name__ == "__main__":
    load_environment()
    print(f"OPENAI_API_KEY is set: {'OPENAI_API_KEY' in os.environ}")
