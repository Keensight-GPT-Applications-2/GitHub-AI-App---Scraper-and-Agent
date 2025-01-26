from fastapi import FastAPI
from models.generated_models.model_1 import AdminlogincheckInput, AdminlogincheckOutput

app = FastAPI()

@app.post("/adminlogincheck")
def process_adminlogincheck(data: AdminlogincheckInput):
    # Example processing
    return AdminlogincheckOutput(result="Processed")