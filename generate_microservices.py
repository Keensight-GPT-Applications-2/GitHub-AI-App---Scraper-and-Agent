import os
from pathlib import Path

def generate_microservices(models_dir="models/generated_models", output_dir="microservices"):
    """
    Generate FastAPI microservices based on Pydantic models.
    """
    models_path = Path(models_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for model_file in models_path.glob("*.py"):
        model_name = model_file.stem  # Get the file name without extension
        with open(model_file, "r", encoding="utf-8") as f:
            model_code = f.read()

        # Extract Input and Output model names from the model code
        lines = model_code.splitlines()
        input_model_name = None
        output_model_name = None

        for line in lines:
            if line.strip().startswith("class") and "Input" in line:
                input_model_name = line.split("class")[1].split("(")[0].strip()
            if line.strip().startswith("class") and "Output" in line:
                output_model_name = line.split("class")[1].split("(")[0].strip()

        if not input_model_name or not output_model_name:
            print(f"Error: Could not determine Input/Output models for {model_name}")
            continue

        # Derive the endpoint name from the Input model (remove "Input" and lowercase it)
        endpoint_name = input_model_name.replace("Input", "").lower()

        # Generate FastAPI route for the model
        endpoint_code = f"""
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from {models_dir.replace("/", ".")}.{model_name} import {input_model_name}, {output_model_name}

app = FastAPI()

@app.post("/{endpoint_name}_service/{endpoint_name}")
def process_{endpoint_name}(data: {input_model_name}):
    try:
        # Example processing
        return {output_model_name}(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
"""

        # Save as a new microservice file
        microservice_file = output_path / f"{endpoint_name}_service.py"
        with open(microservice_file, "w", encoding="utf-8") as mf:
            mf.write(endpoint_code.strip())
            print(f"Generated microservice: {microservice_file}")

if __name__ == "__main__":
    try:
        generate_microservices()
        print("Microservices generated successfully!")
    except Exception as e:
        print(f"An error occurred while generating microservices: {e}")
