from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models.generated_models.model_15 import Remove_tagsInput, Remove_tagsOutput

app = FastAPI()

@app.post("/remove_tags_service/remove_tags")
def process_remove_tags(data: Remove_tagsInput):
    try:
        # Example processing
        return Remove_tagsOutput(result="Processed")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())