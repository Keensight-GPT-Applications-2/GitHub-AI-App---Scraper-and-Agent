from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_18 import Wordcloud2Input, Wordcloud2Output

app = FastAPI()

@app.post("/wordcloud2_service/wordcloud2")
def process_wordcloud2(data: Wordcloud2Input):
    try:
        # Example processing
        return Wordcloud2Output(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())