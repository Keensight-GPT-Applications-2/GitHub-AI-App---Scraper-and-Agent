"""
Auto-generated Pydantic Model for Adminlogincheck
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List, Union
from datetime import datetime
import json



class AdminlogincheckInput(BaseModel):
    username: str
    password: str


class AdminlogincheckOutput(BaseModel):
    status: str
    message: str
    user_id: int
    is_admin: bool


def AdminLoginCheck(username, password) -> Dict[str, Any]:
    """No docstring provided."""
    # Implementation goes here
    return {
        "status": "status value",
        "message": "message value",
        "user_id": 0,
        "is_admin": True
    }
