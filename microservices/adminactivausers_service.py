from fastapi import FastAPI
from models.generated_models.model_4 import AdminactivausersInput, AdminactivausersOutput

app = FastAPI()

@app.post("/adminactivausers")
def process_adminactivausers(data: AdminactivausersInput):
    # Example processing
    return AdminactivausersOutput(result="Processed")