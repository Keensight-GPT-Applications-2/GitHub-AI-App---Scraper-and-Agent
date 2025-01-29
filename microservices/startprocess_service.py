from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_7 import StartprocessInput, StartprocessOutput

app = FastAPI()

@app.post("/startprocess_service/startprocess")
def process_startprocess(data: StartprocessInput):
    try:
        # Example processing
        return StartprocessOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())