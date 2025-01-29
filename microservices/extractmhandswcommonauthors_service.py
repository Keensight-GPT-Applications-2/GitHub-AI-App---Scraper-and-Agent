from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_22 import ExtractmhandswcommonauthorsInput, ExtractmhandswcommonauthorsOutput

app = FastAPI()

@app.post("/extractmhandswcommonauthors_service/extractmhandswcommonauthors")
def process_extractmhandswcommonauthors(data: ExtractmhandswcommonauthorsInput):
    try:
        # Example processing
        return ExtractmhandswcommonauthorsOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())