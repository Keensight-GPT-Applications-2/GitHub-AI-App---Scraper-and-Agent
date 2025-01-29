from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_1 import AdminlogincheckInput, AdminlogincheckOutput

app = FastAPI()

@app.post("/adminlogincheck_service/adminlogincheck")
def process_adminlogincheck(data: AdminlogincheckInput):
    try:
        # Example processing
        return AdminlogincheckOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())