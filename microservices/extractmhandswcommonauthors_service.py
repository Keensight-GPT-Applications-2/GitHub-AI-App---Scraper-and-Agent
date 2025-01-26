from fastapi import FastAPI
from models.generated_models.model_22 import ExtractmhandswcommonauthorsInput, ExtractmhandswcommonauthorsOutput

app = FastAPI()

@app.post("/extractmhandswcommonauthors")
def process_extractmhandswcommonauthors(data: ExtractmhandswcommonauthorsInput):
    # Example processing
    return ExtractmhandswcommonauthorsOutput(result="Processed")