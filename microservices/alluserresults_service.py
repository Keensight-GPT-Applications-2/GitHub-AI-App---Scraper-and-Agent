from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_5 import AlluserresultsInput, AlluserresultsOutput

app = FastAPI()

@app.post("/alluserresults_service/alluserresults")
def process_alluserresults(data: AlluserresultsInput):
    try:
        # Example processing
        return AlluserresultsOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())