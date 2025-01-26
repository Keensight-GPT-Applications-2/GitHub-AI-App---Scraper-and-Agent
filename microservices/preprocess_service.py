from fastapi import FastAPI
from models.generated_models.model_8 import PreprocessInput, PreprocessOutput

app = FastAPI()

@app.post("/preprocess")
def process_preprocess(data: PreprocessInput):
    # Example processing
    return PreprocessOutput(result="Processed")