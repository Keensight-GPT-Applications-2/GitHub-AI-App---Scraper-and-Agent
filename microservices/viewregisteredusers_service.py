from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_3 import ViewregisteredusersInput, ViewregisteredusersOutput

app = FastAPI()

@app.post("/viewregisteredusers_service/viewregisteredusers")
def process_viewregisteredusers(data: ViewregisteredusersInput):
    try:
        # Example processing
        return ViewregisteredusersOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())