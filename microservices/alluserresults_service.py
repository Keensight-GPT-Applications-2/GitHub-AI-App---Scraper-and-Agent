from fastapi import APIRouter, HTTPException
from models.generated_models.Alluserresults import AlluserresultsInput, AlluserresultsOutput
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


@router.post("/alluserresults_service/alluserresults")
def process_alluserresults(data: AlluserresultsInput):
    """
    Dynamically execute AllUserResults from generated models.
    """
    model_path = MODELS_DIR / "Alluserresults.py"
    function_to_call = dynamic_import_function(str(model_path), "AllUserResults")
    if function_to_call:
        try:
            result = function_to_call(**data.dict())
            return AlluserresultsOutput(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Function '{function_name}' execution failed: {str(e)}")
    raise HTTPException(status_code=404, detail="Function 'AllUserResults' not found in generated models")