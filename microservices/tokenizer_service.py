from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_12 import TokenizerInput, TokenizerOutput

app = FastAPI()

@app.post("/tokenizer_service/tokenizer")
def process_tokenizer(data: TokenizerInput):
    try:
        # Example processing
        return TokenizerOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())