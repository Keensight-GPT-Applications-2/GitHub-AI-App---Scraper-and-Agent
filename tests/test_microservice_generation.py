import os
import pytest
from generate_microservices import generate_microservices
from pathlib import Path

def test_microservice_generation():
    """Ensure FastAPI microservices are correctly generated."""
    models_dir = "models/generated_models"
    output_dir = "microservices"

    generate_microservices(models_dir, output_dir)

    # Check if ANY microservice was generated
    generated_services = [f for f in os.listdir(output_dir) if f.endswith("_service.py")]

    assert len(generated_services) > 0, "No microservices were generated!"
    print(f"✅ Generated Microservices: {generated_services}")
