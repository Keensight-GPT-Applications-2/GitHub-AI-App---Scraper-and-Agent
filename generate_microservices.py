import os
import ast
import importlib.util
from pathlib import Path

def extract_functions_with_ast(model_code):
    """
    Extract function names and their parameters from Python code using AST.
    """
    functions = []
    try:
        tree = ast.parse(model_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_name = node.name
                params = [arg.arg for arg in node.args.args if arg.arg != "self"]
                functions.append((function_name, params))
    except SyntaxError as e:
        print(f"❌ AST parsing failed: {e}")
    return functions

def generate_microservices(models_dir="models/generated_models", output_dir="microservices"):
    """
    Generate FastAPI microservices dynamically from extracted functions in models.
    """
    models_path = Path(models_dir).resolve()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    print("🔄 Scanning models directory for .py files...")

    for model_file in models_path.glob("*.py"):
        try:
            model_name = model_file.stem
            repo_name = model_name.lower() + "_service"

            print(f"📄 Processing model: {model_name} ...")

            with open(model_file, "r", encoding="utf-8") as f:
                model_code = f.read()

            functions = extract_functions_with_ast(model_code)

            input_model_name, output_model_name = None, None
            for line in model_code.splitlines():
                if line.strip().startswith("class") and "Input" in line:
                    input_model_name = line.split("class")[1].split("(")[0].strip()
                elif line.strip().startswith("class") and "Output" in line:
                    output_model_name = line.split("class")[1].split("(")[0].strip()

            if not input_model_name or not output_model_name:
                print(f"⚠️ Could not determine Input/Output models for {model_name}. Skipping.")
                continue

            if not functions:
                print(f"⚠️ No functions extracted from {model_name}. Skipping.")
                continue

            print(f"✅ Extracted: Repo = {repo_name}, Input = {input_model_name}, Output = {output_model_name}, Functions = {functions}")

            endpoint_code = f'''
from fastapi import APIRouter, HTTPException
from {models_dir.replace("/", ".")}.{model_name} import {input_model_name}, {output_model_name}
import importlib.util
from pathlib import Path

router = APIRouter()
MODELS_DIR = Path("{models_dir}").resolve()

def dynamic_import_function(module_path, function_name):
    try:
        spec = importlib.util.spec_from_file_location("generated_model", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, function_name, None)
    except Exception as e:
        print(f"❌ Error importing function '{{function_name}}' from '{{module_path}}':", e)
        return None
'''

            for function_name, params in functions:
                endpoint_name = function_name.lower()
                endpoint_code += f'''

@router.post("/{repo_name}/{endpoint_name}")
def process_{endpoint_name}(data: {input_model_name}):
    """
    Dynamically execute {function_name} from generated models.
    """
    model_path = MODELS_DIR / "{model_name}.py"
    function_to_call = dynamic_import_function(str(model_path), "{function_name}")
    if function_to_call:
        try:
            result = function_to_call(**data.dict())
            return {output_model_name}(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Function '{{function_name}}' execution failed: {{str(e)}}")
    raise HTTPException(status_code=404, detail="Function '{function_name}' not found in generated models")
'''

            microservice_file = output_path / f"{repo_name}.py"
            with open(microservice_file, "w", encoding="utf-8") as mf:
                mf.write(endpoint_code.strip())

            print(f"✅ Successfully generated microservice: {microservice_file}")

        except Exception as e:
            print(f"❌ Failed to generate microservice for {model_file.name}: {e}")

if __name__ == "__main__":
    print("🚀 Starting microservice generation with AST-based function extraction...")
    generate_microservices()
    print("✅ Microservices generated successfully!")
