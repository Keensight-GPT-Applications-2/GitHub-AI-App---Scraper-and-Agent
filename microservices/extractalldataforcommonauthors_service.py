from fastapi import FastAPI
from models.generated_models.model_23 import ExtractalldataforcommonauthorsInput, ExtractalldataforcommonauthorsOutput

app = FastAPI()

@app.post("/extractalldataforcommonauthors")
def process_extractalldataforcommonauthors(data: ExtractalldataforcommonauthorsInput):
    # Example processing
    return ExtractalldataforcommonauthorsOutput(result="Processed")