from fastapi import FastAPI
from models.generated_models.model_5 import AlluserresultsInput, AlluserresultsOutput

app = FastAPI()

@app.post("/alluserresults")
def process_alluserresults(data: AlluserresultsInput):
    # Example processing
    return AlluserresultsOutput(result="Processed")