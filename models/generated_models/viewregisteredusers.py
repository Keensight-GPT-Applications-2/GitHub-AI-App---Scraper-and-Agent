"""
Auto-generated Pydantic Model for Viewregisteredusers
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List, Union
from datetime import datetime
import json



class ViewregisteredusersInput(BaseModel):
    request: Any


class ViewregisteredusersOutput(BaseModel):
    users: List[Dict[str, Any]]
    count: int
    success: bool


def ViewRegisteredUsers(request) -> Dict[str, Any]:
    """No docstring provided."""
    # Implementation goes here
    return {
        "users": [],
        "count": 0,
        "success": True
    }
