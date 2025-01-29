from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_20 import ExtractmentalhealthcsvInput, ExtractmentalhealthcsvOutput

app = FastAPI()

@app.post("/extractmentalhealthcsv_service/extractmentalhealthcsv")
def process_extractmentalhealthcsv(data: ExtractmentalhealthcsvInput):
    try:
        # Example processing
        return ExtractmentalhealthcsvOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())