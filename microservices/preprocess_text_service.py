from fastapi import FastAPI
from models.generated_models.model_14 import Preprocess_textInput, Preprocess_textOutput

app = FastAPI()

@app.post("/preprocess_text")
def process_preprocess_text(data: Preprocess_textInput):
    # Example processing
    return Preprocess_textOutput(result="Processed")