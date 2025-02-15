"""
Auto-generated Pydantic Model: viewregisteredusers
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ViewregisteredusersInput(BaseModel):
    request: Dict[str, Any]

class ViewregisteredusersOutput(BaseModel):
    result: Optional[Any] = None