"""
Auto-generated Pydantic Models
File: model_13.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class StartprocessInput(BaseModel):
    self: Any  # Default type is 'Any'

class StartprocessOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted