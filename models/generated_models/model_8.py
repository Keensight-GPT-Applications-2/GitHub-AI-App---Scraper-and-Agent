"""
Auto-generated Pydantic Models
File: model_8.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class PreprocessInput(BaseModel):
    self: Any  # Default type is 'Any'
    tweet: Any  # Default type is 'Any'

class PreprocessOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted