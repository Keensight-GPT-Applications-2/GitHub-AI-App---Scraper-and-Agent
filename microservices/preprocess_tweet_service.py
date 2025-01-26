from fastapi import FastAPI
from models.generated_models.model_10 import Preprocess_tweetInput, Preprocess_tweetOutput

app = FastAPI()

@app.post("/preprocess_tweet")
def process_preprocess_tweet(data: Preprocess_tweetInput):
    # Example processing
    return Preprocess_tweetOutput(result="Processed")