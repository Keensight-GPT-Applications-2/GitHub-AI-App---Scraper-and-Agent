"""
Auto-generated Pydantic Model: Alluserresults
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import json

class AlluserresultsInput(BaseModel):
    request: Any

class AlluserresultsOutput(BaseModel):
    result: Optional[Any] = None

def AllUserResults(request) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success'}