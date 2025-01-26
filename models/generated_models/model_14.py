"""
Auto-generated Pydantic Models
File: model_14.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class Preprocess_textInput(BaseModel):
    sen: Any  # Default type is 'Any'

class Preprocess_textOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted