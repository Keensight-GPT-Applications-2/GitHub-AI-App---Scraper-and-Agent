"""
Auto-generated Pydantic Model: alluserresults
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class AlluserresultsInput(BaseModel):
    request: Dict[str, Any]

class AlluserresultsOutput(BaseModel):
    result: Optional[Any] = None