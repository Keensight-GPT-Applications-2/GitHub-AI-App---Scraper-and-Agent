"""
Auto-generated Pydantic Model: adminhome
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class AdminhomeInput(BaseModel):
    request: Dict[str, Any]

class AdminhomeOutput(BaseModel):
    result: Optional[Any] = None