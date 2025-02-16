import os
import importlib.util
from pathlib import Path

def generate_microservices(models_dir="models/generated_models", output_dir="microservices"):
    """
    Generate FastAPI microservices that dynamically execute functions from generated models.
    """
    models_path = Path(models_dir).resolve()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    print("🔄 Scanning models directory for .py files...")

    for model_file in models_path.glob("*.py"):
        model_name = model_file.stem  # Get the filename without extension
        repo_name = model_name.lower() + "_service"  # Keep full name

        print(f"📄 Processing model: {model_name} ...")

        with open(model_file, "r", encoding="utf-8") as f:
            model_code = f.read()

        # Extract Input and Output model names from the model code
        input_model_name, output_model_name = None, None

        for line in model_code.splitlines():
            if line.strip().startswith("class") and "Input" in line:
                input_model_name = line.split("class")[1].split("(")[0].strip()
            if line.strip().startswith("class") and "Output" in line:
                output_model_name = line.split("class")[1].split("(")[0].strip()

        if not input_model_name or not output_model_name:
            print(f"⚠️ Error: Could not determine Input/Output models for {model_name}")
            continue

        print(f"✅ Extracted: Repo = {repo_name}, Input = {input_model_name}, Output = {output_model_name}")

        # Define the microservice FastAPI code
        endpoint_code = f"""
from fastapi import FastAPI, APIRouter, HTTPException
from {models_dir.replace("/", ".")}.{model_name} import {input_model_name}, {output_model_name}
import importlib.util
import os
from pathlib import Path

router = APIRouter()

MODELS_DIR = Path("{models_dir}").resolve()

def dynamic_import_function(module_path, function_name):
    \"\"\"Dynamically import a function from a generated model.\"\"\" 
    spec = importlib.util.spec_from_file_location("generated_model", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    available_functions = [attr for attr in dir(module) if callable(getattr(module, attr))]
    print(f"🔍 Available functions in {{module_path}}: {{available_functions}}")
    
    return getattr(module, function_name, None)

@router.post("/{repo_name}/{input_model_name.lower()}")
def process_{input_model_name.lower()}(data: {input_model_name}):
    \"\"\"Dynamically execute {input_model_name} from generated models.\"\"\" 
    model_path = MODELS_DIR / "{model_name}.py"

    function_to_call = dynamic_import_function(str(model_path), "{input_model_name}")
    if function_to_call:
        print(f"✅ Function {input_model_name} found in: {{model_path}}")
        result = function_to_call(**data.dict())  # Pass Pydantic model data as function arguments
        return {output_model_name}(result=result)

    raise HTTPException(status_code=404, detail="Function '{input_model_name}' not found in generated models")

app = FastAPI()
app.include_router(router)
"""

        # Save as a single microservice file per repo
        microservice_file = output_path / f"{repo_name}.py"
        with open(microservice_file, "w", encoding="utf-8") as mf:
            mf.write(endpoint_code.strip())
            print(f"✅ Successfully generated microservice: {microservice_file}")

if __name__ == "__main__":
    print("🚀 Starting microservice generation...")
    generate_microservices()
    print("✅ Microservices generated successfully!")
