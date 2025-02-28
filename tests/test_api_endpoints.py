import pytest
from fastapi.testclient import TestClient
from microservices.adminactivausers_service import router  # ✅ Import router instead of app
from fastapi import FastAPI

# ✅ Create a FastAPI app and include the router
app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_valid_api_call():
    """Test if the API correctly processes valid requests."""
    response = client.post("/adminactivausers_service/adminactivausers", json={"request": {"key": "value"}})
    assert response.status_code == 200  # Ensure the request succeeds

def test_invalid_api_call():
    """Test if the API handles invalid requests."""
    response = client.post("/adminactivausers_service/adminactivausers", json={})  # Missing 'request' key
    assert response.status_code == 422  # Pydantic should reject invalid input
