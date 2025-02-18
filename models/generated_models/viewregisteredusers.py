"""
Auto-generated Pydantic Model: viewregisteredusers
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ViewregisteredusersInput(BaseModel):
    request: Dict[str, Any]

class ViewregisteredusersOutput(BaseModel):
    result: Optional[Any] = None

def ViewRegisteredUsers(request) -> Optional[Any]:
    """No docstring provided."""
    return {'status': 'success', 'processed_data': {param: param for param in [request]}}