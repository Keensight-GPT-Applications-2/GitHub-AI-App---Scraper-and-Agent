from fastapi import FastAPI
from models.generated_models.model_15 import Remove_tagsInput, Remove_tagsOutput

app = FastAPI()

@app.post("/remove_tags")
def process_remove_tags(data: Remove_tagsInput):
    # Example processing
    return Remove_tagsOutput(result="Processed")