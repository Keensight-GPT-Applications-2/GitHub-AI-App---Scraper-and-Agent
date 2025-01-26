"""
Auto-generated Pydantic Models
File: model_2.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class AdminhomeInput(BaseModel):
    request: Any  # Default type is 'Any'

class AdminhomeOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted