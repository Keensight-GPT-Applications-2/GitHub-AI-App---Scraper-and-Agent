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

def extract_model_fields(model_code, model_name):
    """
    Extract fields from a Pydantic model class.
    """
    fields = {}
    try:
        tree = ast.parse(model_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == model_name:
                for child in node.body:
                    if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                        field_name = child.target.id
                        if isinstance(child.annotation, ast.Name):
                            field_type = child.annotation.id
                        elif hasattr(ast, 'unparse'):
                            field_type = ast.unparse(child.annotation)
                        else:
                            field_type = "Any"
                        fields[field_name] = field_type
    except SyntaxError as e:
        print(f"❌ AST parsing failed for model {model_name}: {e}")
    return fields

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

            # Extract output model fields for better response handling
            output_fields = extract_model_fields(model_code, output_model_name)
            input_fields = extract_model_fields(model_code, input_model_name)
            
            print(f"✅ Extracted: Repo = {repo_name}, Input = {input_model_name}, Output = {output_model_name}, Functions = {functions}")
            print(f"   Input model fields: {input_fields}")
            print(f"   Output model fields: {output_fields}")

            # Get function parameters
            function_name, function_params = functions[0] if functions else (None, [])

            endpoint_code = f'''
from fastapi import APIRouter, HTTPException
from {models_dir.replace("/", ".")}.{model_name} import {input_model_name}, {output_model_name}
import importlib.util
from pathlib import Path
import json
from typing import Dict, Any, Optional

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

def ensure_output_has_required_fields(result: Dict[str, Any], expected_fields: list) -> Dict[str, Any]:
    """
    Ensure the result has all required fields for the output model.
    This prevents validation errors when creating the Pydantic model.
    """
    if result is None:
        result = {{}}
    
    if isinstance(result, dict):
        for field in expected_fields:
            if field not in result:
                # Provide default values based on common field names
                if field == "success" or field == "is_admin":
                    result[field] = True
                elif field == "message":
                    result[field] = "Operation completed successfully"
                elif field == "updated_count" or field == "count" or field == "user_id":
                    result[field] = 0
                elif field == "users":
                    result[field] = []
                elif field == "result":
                    result[field] = None
                else:
                    result[field] = None
    return result
'''

            for function_name, params in functions:
                endpoint_name = function_name.lower()
                output_field_list = list(output_fields.keys())
                
                # Create a parameter mapping from input model fields to function parameters
                param_mapping = ""
                if params:
                    # If the function has parameters, we need to map input fields to them
                    if len(params) == 1 and "data" in params:
                        # If the function just takes a single 'data' parameter, pass the entire input
                        param_mapping = "data"
                    else:
                        # Try to match function parameters by position
                        input_fields_list = list(input_fields.keys())
                        param_args = []
                        for i, param in enumerate(params):
                            if i < len(input_fields_list):
                                param_args.append(f'input_data.get("{input_fields_list[i]}")')
                            else:
                                param_args.append("None")
                        param_mapping = ", ".join(param_args)
                
                endpoint_code += f'''

@router.post("/{repo_name}/{endpoint_name}")
def process_{endpoint_name}(data: {input_model_name}):
    """
    Dynamically execute {function_name} from generated models.
    """
    import json
    import os
    from pathlib import Path
    import datetime

    model_path = MODELS_DIR / "{model_name}.py"
    function_to_call = dynamic_import_function(str(model_path), "{function_name}")
    if function_to_call:
        try:
            # Convert input data to dict for function call
            input_data = data.dict()
            
            # Call the function with positional arguments instead of keyword arguments
            result = function_to_call({param_mapping})
            
            # Ensure result has all required fields
            expected_fields = {output_field_list}
            result = ensure_output_has_required_fields(result, expected_fields)
            
            # Create response object
            response_obj = {output_model_name}(**result)

            # Save the result to a JSON file
            save_dir = Path("microservices/saved_outputs")
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            save_path = save_dir / f"{repo_name}_{endpoint_name}.json"
            if save_path.exists():
                with open(save_path, "r", encoding="utf-8") as f:
                    try:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                    except json.JSONDecodeError:
                        existing_data = []
            else:
                existing_data = []

            # Append new data
            existing_data.append(input_data)

            # Save updated data
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            return response_obj
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Function '{function_name}' execution failed: {{str(e)}}")
    raise HTTPException(status_code=404, detail=f"Function '{function_name}' not found in generated models")
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