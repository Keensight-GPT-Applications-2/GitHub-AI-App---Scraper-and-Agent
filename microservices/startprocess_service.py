from fastapi import FastAPI
from models.generated_models.model_7 import StartprocessInput, StartprocessOutput

app = FastAPI()

@app.post("/startprocess")
def process_startprocess(data: StartprocessInput):
    # Example processing
    return StartprocessOutput(result="Processed")