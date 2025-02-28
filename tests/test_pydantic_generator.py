import pytest
from models.pydantic_generator import generate_pydantic_models

def test_pydantic_model_generation():
    """Test if Pydantic models are generated correctly."""
    parsed_data = {
        "file1.py": {
            "functions": [
                {
                    "name": "process_data",
                    "parameters": ["text"],
                    "return_type": "str",
                    "docstring": "Processes text and returns output."
                }
            ]
        }
    }

    models = generate_pydantic_models(parsed_data)
    assert "ProcessData" in models  # Updated to PascalCase
    assert "class ProcessDataInput" in models["ProcessData"]
    assert "class ProcessDataOutput" in models["ProcessData"]

