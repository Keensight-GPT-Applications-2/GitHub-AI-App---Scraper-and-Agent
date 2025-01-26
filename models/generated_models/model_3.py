"""
Auto-generated Pydantic Models
File: model_3.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class ViewregisteredusersInput(BaseModel):
    request: Any  # Default type is 'Any'

class ViewregisteredusersOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted