"""
Auto-generated Pydantic Model: detecttypes
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class DetecttypesInput(BaseModel):
    tweet: str

class DetecttypesOutput(BaseModel):
    result: Optional[Any] = None