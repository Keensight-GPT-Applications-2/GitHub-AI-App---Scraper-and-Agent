from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_11 import Tokenizer_porterInput, Tokenizer_porterOutput

app = FastAPI()

@app.post("/tokenizer_porter_service/tokenizer_porter")
def process_tokenizer_porter(data: Tokenizer_porterInput):
    try:
        # Example processing
        return Tokenizer_porterOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())