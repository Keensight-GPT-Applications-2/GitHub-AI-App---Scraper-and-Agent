from fastapi import FastAPI
from models.generated_models.model_18 import Wordcloud2Input, Wordcloud2Output

app = FastAPI()

@app.post("/wordcloud2")
def process_wordcloud2(data: Wordcloud2Input):
    # Example processing
    return Wordcloud2Output(result="Processed")