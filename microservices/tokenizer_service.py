from fastapi import FastAPI
from models.generated_models.model_12 import TokenizerInput, TokenizerOutput

app = FastAPI()

@app.post("/tokenizer")
def process_tokenizer(data: TokenizerInput):
    # Example processing
    return TokenizerOutput(result="Processed")