from fastapi import FastAPI
from models.generated_models.model_11 import Tokenizer_porterInput, Tokenizer_porterOutput

app = FastAPI()

@app.post("/tokenizer_porter")
def process_tokenizer_porter(data: Tokenizer_porterInput):
    # Example processing
    return Tokenizer_porterOutput(result="Processed")