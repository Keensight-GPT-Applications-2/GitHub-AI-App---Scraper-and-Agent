"""
Auto-generated Pydantic Models
File: model_9.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class DetecttypesInput(BaseModel):
    selfself: Any  # Default type is 'Any'
    tweet: Any  # Default type is 'Any'

class DetecttypesOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted