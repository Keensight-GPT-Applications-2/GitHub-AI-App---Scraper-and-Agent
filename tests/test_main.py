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

def test_specific_model():
    """
    Test fetching the schema of a specific model dynamically.
    """
    # Fetch available models from the /models endpoint
    models_response = client.get("/models")
    assert models_response.status_code == 200

    models = models_response.json().get("models", [])
    assert isinstance(models, list), "Expected 'models' to be a list"

    # Iterate through each model name and fetch its schema
    for model_name in models:
        response = client.get(f"/models/{model_name}")
        if response.status_code == 200:
            assert "title" in response.json()
            assert "type" in response.json()
        else:
            assert response.status_code == 404
            assert "error" in response.json()

def test_invalid_model():
    """
    Test fetching the schema of an invalid/nonexistent model.
    """
    invalid_model_name = "nonexistent_model"
    response = client.get(f"/models/{invalid_model_name}")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert response.json()["detail"] == f"Model {invalid_model_name} not found"


def test_invalid_input():
    """
    Test sending invalid input to a model endpoint.
    """
    models_response = client.get("/models")
    assert models_response.status_code == 200

    models = models_response.json().get("models", [])
    assert isinstance(models, list), "Expected 'models' to be a list"

    if models:
        model_name = models[0]  # Example: "AdminlogincheckInput"
        endpoint_name = model_name.replace("Input", "").lower()  # Remove "Input" and lowercase
        invalid_payload = {"invalid_field": "test"}  # Missing required fields
        response = client.post(f"/{endpoint_name}_service/{endpoint_name}", json=invalid_payload)
        
        print(f"Testing endpoint: /{endpoint_name}_service/{endpoint_name}")
        print(f"Response status: {response.status_code}, Response body: {response.json()}")

        assert response.status_code == 422  # Expect validation failure


