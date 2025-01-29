from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_23 import ExtractalldataforcommonauthorsInput, ExtractalldataforcommonauthorsOutput

app = FastAPI()

@app.post("/extractalldataforcommonauthors_service/extractalldataforcommonauthors")
def process_extractalldataforcommonauthors(data: ExtractalldataforcommonauthorsInput):
    try:
        # Example processing
        return ExtractalldataforcommonauthorsOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())