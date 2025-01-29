from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_9 import DetecttypesInput, DetecttypesOutput

app = FastAPI()

@app.post("/detecttypes_service/detecttypes")
def process_detecttypes(data: DetecttypesInput):
    try:
        # Example processing
        return DetecttypesOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())