"""
Auto-generated Pydantic Model: preprocess
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class PreprocessInput(BaseModel):
    tweet: Any

class PreprocessOutput(BaseModel):
    result: Optional[Any] = None

def preProcess(tweet) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success', 'processed_data': {param: param for param in [tweet]}}