from fastapi import FastAPI
from models.generated_models.model_2 import AdminhomeInput, AdminhomeOutput

app = FastAPI()

@app.post("/adminhome")
def process_adminhome(data: AdminhomeInput):
    # Example processing
    return AdminhomeOutput(result="Processed")