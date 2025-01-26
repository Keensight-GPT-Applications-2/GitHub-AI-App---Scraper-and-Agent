from fastapi import FastAPI
from models.generated_models.model_17 import WordcloudInput, WordcloudOutput

app = FastAPI()

@app.post("/wordcloud")
def process_wordcloud(data: WordcloudInput):
    # Example processing
    return WordcloudOutput(result="Processed")