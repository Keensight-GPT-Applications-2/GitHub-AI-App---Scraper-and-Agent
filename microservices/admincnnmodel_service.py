from fastapi import FastAPI
from models.generated_models.model_6 import AdmincnnmodelInput, AdmincnnmodelOutput

app = FastAPI()

@app.post("/admincnnmodel")
def process_admincnnmodel(data: AdmincnnmodelInput):
    # Example processing
    return AdmincnnmodelOutput(result="Processed")