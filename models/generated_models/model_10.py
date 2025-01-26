"""
Auto-generated Pydantic Models
File: model_10.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class Preprocess_tweetInput(BaseModel):
    text: Any  # Default type is 'Any'

class Preprocess_tweetOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted