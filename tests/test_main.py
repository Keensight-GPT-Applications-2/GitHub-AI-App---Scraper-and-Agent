import os
import sys
import pytest
from httpx import AsyncClient
from pathlib import Path

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

API_KEY = os.getenv("API_KEY")

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/", headers={"X-API-KEY": API_KEY})  # ✅ Add API Key
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Pydantic Microservice!"}

@pytest.mark.asyncio
async def test_list_models():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/models", headers={"X-API-KEY": API_KEY})
        assert response.status_code == 200
        assert "models" in response.json()

@pytest.mark.asyncio
async def test_get_model_valid():
    model_name = "TestModelInput"  # Replace with a valid model name
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/models/{model_name}", headers={"X-API-KEY": API_KEY})
        assert response.status_code == 200
        assert "schema" in response.json()

@pytest.mark.asyncio
async def test_get_model_invalid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/models/invalid_model", headers={"X-API-KEY": API_KEY})
        assert response.status_code == 404
        assert response.json()["error"] == "Model invalid_model not found"

@pytest.mark.asyncio
async def test_authentication_failure():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/models")
        assert response.status_code == 403  # Unauthorized

@pytest.mark.asyncio
async def test_rate_limit():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        for _ in range(11):  # Exceeding 10 requests per minute
            response = await ac.get("/models", headers={"X-API-KEY": API_KEY})
        assert response.status_code == 429  # Too Many Requests
