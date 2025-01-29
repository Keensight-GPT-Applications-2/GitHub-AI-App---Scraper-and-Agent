from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_10 import Preprocess_tweetInput, Preprocess_tweetOutput

app = FastAPI()

@app.post("/preprocess_tweet_service/preprocess_tweet")
def process_preprocess_tweet(data: Preprocess_tweetInput):
    try:
        # Example processing
        return Preprocess_tweetOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())