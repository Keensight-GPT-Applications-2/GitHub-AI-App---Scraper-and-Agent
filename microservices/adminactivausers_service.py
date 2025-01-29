from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_4 import AdminactivausersInput, AdminactivausersOutput

app = FastAPI()

@app.post("/adminactivausers_service/adminactivausers")
def process_adminactivausers(data: AdminactivausersInput):
    try:
        # Example processing
        return AdminactivausersOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())