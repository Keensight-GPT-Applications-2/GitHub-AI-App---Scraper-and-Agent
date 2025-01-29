from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_6 import AdmincnnmodelInput, AdmincnnmodelOutput

app = FastAPI()

@app.post("/admincnnmodel_service/admincnnmodel")
def process_admincnnmodel(data: AdmincnnmodelInput):
    try:
        # Example processing
        return AdmincnnmodelOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())