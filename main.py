import logging
from fastapi import FastAPI, HTTPException
from pathlib import Path
import importlib.util
from importlib import import_module
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

# Centralized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file
        logging.StreamHandler()         # Logs to the console
    ]
)

app = FastAPI()

# Add CORS middleware configuration here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamically load Pydantic models from generated_models
def load_generated_models():
    models = {}
    models_dir = Path(__file__).resolve().parent / "models/generated_models"

    if not models_dir.exists():
        logging.error("Generated models directory does not exist.")
        return models

    for model_file in models_dir.glob("*.py"):
        logging.info(f"Loading model from: {model_file.name}")
        module_name = model_file.stem
        spec = importlib.util.spec_from_file_location(module_name, model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Dynamically load all classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseModel) and attr is not BaseModel:
                models[attr_name] = attr

    logging.info(f"Loaded models: {list(models.keys())}")
    return models

# Dynamically include all microservices
def include_microservices(app):
    microservices_dir = Path(__file__).resolve().parent / "microservices"

    if not microservices_dir.exists():
        logging.error("Microservices directory does not exist.")
        return

    for service_file in microservices_dir.glob("*.py"):
        service_name = service_file.stem
        try:
            logging.info(f"Including service: {service_name}")
            module = import_module(f"microservices.{service_name}")
            if hasattr(module, "app") and hasattr(module.app, "router"):
                app.include_router(module.app.router, prefix=f"/{service_name}")
        except Exception as e:
            logging.error(f"Failed to include service {service_name}: {e}")

# Load models
generated_models = load_generated_models()

# Include microservices
include_microservices(app)

@app.get("/")
def root():
    return {"message": "Welcome to the Pydantic Microservice!"}

@app.get("/models")
def list_models():
    models = load_generated_models()
    logging.info("Loaded models: %s", models.keys())  # Debug
    return {"models": list(models.keys())}

@app.get("/models/{model_name}")
def get_model(model_name: str):
    logging.info(f"Requested model name: {model_name}")
    logging.info(f"Available models: {list(generated_models.keys())}")
    if model_name in generated_models:
        return generated_models[model_name].schema()
    else:
        # Return a 404 status code for invalid models
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
