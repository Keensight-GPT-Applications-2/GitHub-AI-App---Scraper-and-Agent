from fastapi import FastAPI
from models.generated_models.model_3 import ViewregisteredusersInput, ViewregisteredusersOutput

app = FastAPI()

@app.post("/viewregisteredusers")
def process_viewregisteredusers(data: ViewregisteredusersInput):
    # Example processing
    return ViewregisteredusersOutput(result="Processed")