"""
Auto-generated Pydantic Model: Detecttypes
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import json

class DetecttypesInput(BaseModel):
    tweet: str

class DetecttypesOutput(BaseModel):
    result: Optional[Any] = None

def detectTypes(selfself, tweet) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success'}