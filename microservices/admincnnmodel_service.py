from fastapi import APIRouter, HTTPException
from models.generated_models.Admincnnmodel import AdmincnnmodelInput, AdmincnnmodelOutput
import importlib.util
from pathlib import Path

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


@router.post("/admincnnmodel_service/admincnnmodel")
def process_admincnnmodel(data: AdmincnnmodelInput):
    """
    Dynamically execute adminCNNModel from generated models.
    """
    model_path = MODELS_DIR / "Admincnnmodel.py"
    function_to_call = dynamic_import_function(str(model_path), "adminCNNModel")
    if function_to_call:
        try:
            result = function_to_call(**data.dict())
            return AdmincnnmodelOutput(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Function '{function_name}' execution failed: {str(e)}")
    raise HTTPException(status_code=404, detail="Function 'adminCNNModel' not found in generated models")