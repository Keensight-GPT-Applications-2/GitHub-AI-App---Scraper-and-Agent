import sys
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Pydantic Microservice!"}

def test_models():
    response = client.get("/models")
    assert response.status_code == 200
    assert "models" in response.json()
