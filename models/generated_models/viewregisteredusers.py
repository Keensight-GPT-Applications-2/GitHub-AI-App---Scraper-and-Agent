"""
Auto-generated Pydantic Model: Viewregisteredusers
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import json

class ViewregisteredusersInput(BaseModel):
    request: Dict[str, Any]

class ViewregisteredusersOutput(BaseModel):
    result: Optional[Any] = None

def ViewRegisteredUsers(request) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success'}