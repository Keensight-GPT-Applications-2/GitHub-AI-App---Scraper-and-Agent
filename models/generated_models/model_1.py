"""
Auto-generated Pydantic Models
File: model_1.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class AdminlogincheckInput(BaseModel):
    request: Any  # Default type is 'Any'

class AdminlogincheckOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted