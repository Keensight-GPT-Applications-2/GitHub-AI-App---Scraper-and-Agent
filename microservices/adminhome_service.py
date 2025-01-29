from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_2 import AdminhomeInput, AdminhomeOutput

app = FastAPI()

@app.post("/adminhome_service/adminhome")
def process_adminhome(data: AdminhomeInput):
    try:
        # Example processing
        return AdminhomeOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())