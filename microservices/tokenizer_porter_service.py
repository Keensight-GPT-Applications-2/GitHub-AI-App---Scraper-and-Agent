from fastapi import FastAPI, APIRouter, HTTPException
from models.generated_models.tokenizer_porter import Tokenizer_porterInput, Tokenizer_porterOutput
import importlib.util
import os
from pathlib import Path

router = APIRouter()

MODELS_DIR = Path("models/generated_models").resolve()

def dynamic_import_function(module_path, function_name):
    """Dynamically import a function from a generated model.""" 
    spec = importlib.util.spec_from_file_location("generated_model", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    available_functions = [attr for attr in dir(module) if callable(getattr(module, attr))]
    print(f"🔍 Available functions in {module_path}: {available_functions}")
    
    return getattr(module, function_name, None)

@router.post("/tokenizer_porter_service/tokenizer_porterinput")
def process_tokenizer_porterinput(data: Tokenizer_porterInput):
    """Dynamically execute Tokenizer_porterInput from generated models.""" 
    model_path = MODELS_DIR / "tokenizer_porter.py"

    function_to_call = dynamic_import_function(str(model_path), "Tokenizer_porterInput")
    if function_to_call:
        print(f"✅ Function Tokenizer_porterInput found in: {model_path}")
        result = function_to_call(**data.dict())  # Pass Pydantic model data as function arguments
        return Tokenizer_porterOutput(result=result)

    raise HTTPException(status_code=404, detail="Function 'Tokenizer_porterInput' not found in generated models")

app = FastAPI()
app.include_router(router)