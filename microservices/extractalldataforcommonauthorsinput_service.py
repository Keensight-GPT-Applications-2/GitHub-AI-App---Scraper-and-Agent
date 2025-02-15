from fastapi import FastAPI, HTTPException
from models.generated_models.extractalldataforcommonauthors import ExtractalldataforcommonauthorsInput, ExtractalldataforcommonauthorsOutput
import importlib.util
import os
from pathlib import Path

app = FastAPI()

MODELS_DIR = Path("models/generated_models").resolve()

def dynamic_import_function(module_path, function_name):
    """Dynamically import a function from a generated model.""" 
    spec = importlib.util.spec_from_file_location("generated_model", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    available_functions = [attr for attr in dir(module) if callable(getattr(module, attr))]
    print(f"🔍 Available functions in {module_path}: {available_functions}")
    
    return getattr(module, function_name, None)

@app.post("/extractalldataforcommonauthorsinput_service/extractalldataforcommonauthorsinput")
def process_extractalldataforcommonauthorsinput(data: ExtractalldataforcommonauthorsInput):
    """Dynamically execute the function from generated models."""
    # Locate the Python files in models directory
    model_path = MODELS_DIR
    python_files = list(model_path.rglob("*.py"))

    for file_path in python_files:
        function_to_call = dynamic_import_function(str(file_path), "ExtractalldataforcommonauthorsInput")
        if function_to_call:
            print(f"✅ Function ExtractalldataforcommonauthorsInput found in: {file_path}")
            result = function_to_call(**data.dict())  # Pass Pydantic model data as function arguments
            return ExtractalldataforcommonauthorsOutput(result=result)

    raise HTTPException(status_code=404, detail="Function 'ExtractalldataforcommonauthorsInput' not found in generated models")