from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_16 import ExtractmentalhealthInput, ExtractmentalhealthOutput

app = FastAPI()

@app.post("/extractmentalhealth_service/extractmentalhealth")
def process_extractmentalhealth(data: ExtractmentalhealthInput):
    try:
        # Example processing
        return ExtractmentalhealthOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())