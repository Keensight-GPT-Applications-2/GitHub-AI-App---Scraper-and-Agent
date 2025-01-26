from fastapi import FastAPI
from models.generated_models.model_9 import DetecttypesInput, DetecttypesOutput

app = FastAPI()

@app.post("/detecttypes")
def process_detecttypes(data: DetecttypesInput):
    # Example processing
    return DetecttypesOutput(result="Processed")