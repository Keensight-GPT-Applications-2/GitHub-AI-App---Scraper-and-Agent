"""
Auto-generated Pydantic Model: adminactivausers
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class AdminactivausersInput(BaseModel):
    request: Dict[str, Any]

class AdminactivausersOutput(BaseModel):
    result: Optional[Any] = None