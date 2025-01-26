from fastapi import FastAPI
from models.generated_models.model_20 import ExtractmentalhealthcsvInput, ExtractmentalhealthcsvOutput

app = FastAPI()

@app.post("/extractmentalhealthcsv")
def process_extractmentalhealthcsv(data: ExtractmentalhealthcsvInput):
    # Example processing
    return ExtractmentalhealthcsvOutput(result="Processed")