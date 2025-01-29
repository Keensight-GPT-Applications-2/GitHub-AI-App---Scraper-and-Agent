from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_14 import Preprocess_textInput, Preprocess_textOutput

app = FastAPI()

@app.post("/preprocess_text_service/preprocess_text")
def process_preprocess_text(data: Preprocess_textInput):
    try:
        # Example processing
        return Preprocess_textOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())