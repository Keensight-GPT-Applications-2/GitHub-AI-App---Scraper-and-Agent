"""
Auto-generated Pydantic Models
File: model_19.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class ExtractsuicidalwatchInput(BaseModel):
    self: Any  # Default type is 'Any'
    reddit: Any  # Default type is 'Any'

class ExtractsuicidalwatchOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted