from fastapi import FastAPI
from pathlib import Path
import importlib.util

from pydantic import BaseModel

app = FastAPI()

# Dynamically load Pydantic models from generated_models
def load_generated_models():
    models = {}
    models_dir = Path("models/generated_models")
    
    if not models_dir.exists():
        print("Generated models directory does not exist.")
        return models

    for model_file in models_dir.glob("*.py"):
        print(f"Loading model from: {model_file.name}")
        module_name = model_file.stem
        spec = importlib.util.spec_from_file_location(module_name, model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
                models[attr_name] = attr

    return models

# Load models
generated_models = load_generated_models()

@app.get("/")
def root():
    return {"message": "Welcome to the Pydantic Microservice!"}

@app.get("/models")
def list_models():
    models = load_generated_models()
    print("Loaded models:", models.keys())  # Debug
    return {"models": list(models.keys())}

@app.get("/models/{model_name}")
def get_model_fields(model_name: str):
    """Retrieve the fields of a specific Pydantic model."""
    model = generated_models.get(model_name)
    if not model:
        return {"error": f"Model {model_name} not found"}
    
    fields = {name: str(field) for name, field in model.__dict__.items() if not name.startswith("__")}
    return {"model_name": model_name, "fields": fields}
