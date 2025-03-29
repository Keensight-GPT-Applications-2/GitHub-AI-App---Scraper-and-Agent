"""
Auto-generated Pydantic Model: Adminhome
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import json

class AdminhomeInput(BaseModel):
    request: Any

class AdminhomeOutput(BaseModel):
    result: Optional[Any] = None

def AdminHome(request) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success'}