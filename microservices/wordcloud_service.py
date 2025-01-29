from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_17 import WordcloudInput, WordcloudOutput

app = FastAPI()

@app.post("/wordcloud_service/wordcloud")
def process_wordcloud(data: WordcloudInput):
    try:
        # Example processing
        return WordcloudOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())