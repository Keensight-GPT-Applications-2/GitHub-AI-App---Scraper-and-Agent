from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_8 import PreprocessInput, PreprocessOutput

app = FastAPI()

@app.post("/preprocess_service/preprocess")
def process_preprocess(data: PreprocessInput):
    try:
        # Example processing
        return PreprocessOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())