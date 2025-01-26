"""
Auto-generated Pydantic Models
File: model_6.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class AdmincnnmodelInput(BaseModel):
    request: Any  # Default type is 'Any'

class AdmincnnmodelOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted