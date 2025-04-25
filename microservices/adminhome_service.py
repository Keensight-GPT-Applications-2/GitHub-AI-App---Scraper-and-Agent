from fastapi import APIRouter, HTTPException
from models.generated_models.Adminhome import AdminhomeInput, AdminhomeOutput
import importlib.util
from pathlib import Path
import json
from typing import Dict, Any, Optional

router = APIRouter()
MODELS_DIR = Path("models/generated_models").resolve()

def dynamic_import_function(module_path, function_name):
    try:
        spec = importlib.util.spec_from_file_location("generated_model", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, function_name, None)
    except Exception as e:
        print(f"❌ Error importing function '{function_name}' from '{module_path}':", e)
        return None

def ensure_output_has_required_fields(result: Dict[str, Any], expected_fields: list) -> Dict[str, Any]:
    """
    Ensure the result has all required fields for the output model.
    This prevents validation errors when creating the Pydantic model.
    """
    if result is None:
        result = {}
    
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


@router.post("/adminhome_service/adminhome")
def process_adminhome(data: AdminhomeInput):
    """
    Dynamically execute AdminHome from generated models.
    """
    import json
    import os
    from pathlib import Path
    import datetime

    model_path = MODELS_DIR / "Adminhome.py"
    function_to_call = dynamic_import_function(str(model_path), "AdminHome")
    if function_to_call:
        try:
            # Convert input data to dict for function call
            input_data = data.dict()
            
            # Call the function with positional arguments instead of keyword arguments
            result = function_to_call(input_data.get("request"))
            
            # Ensure result has all required fields
            expected_fields = ['result']
            result = ensure_output_has_required_fields(result, expected_fields)
            
            # Create response object
            response_obj = AdminhomeOutput(**result)

            # Save the result to a JSON file
            save_dir = Path("microservices/saved_outputs")
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            save_path = save_dir / f"adminhome_service_adminhome.json"
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
            raise HTTPException(status_code=500, detail=f"Function 'AdminHome' execution failed: {str(e)}")
    raise HTTPException(status_code=404, detail=f"Function 'AdminHome' not found in generated models")