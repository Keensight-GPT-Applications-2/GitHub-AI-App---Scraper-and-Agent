"""
Auto-generated Pydantic Model: Preprocess
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import json

class PreprocessInput(BaseModel):
    tweet: str

class PreprocessOutput(BaseModel):
    result: Optional[Any] = None

def preProcess(tweet) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success'}