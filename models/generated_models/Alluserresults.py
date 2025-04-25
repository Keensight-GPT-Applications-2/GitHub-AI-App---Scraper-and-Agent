"""
Auto-generated Pydantic Model for Alluserresults
"""
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List, Union
from datetime import datetime
import json



class AlluserresultsInput(BaseModel):
    request: Any


class AlluserresultsOutput(BaseModel):
    users: List[Dict[str, Any]]
    count: int
    success: bool


def AllUserResults(request) -> Dict[str, Any]:
    """No docstring provided."""
    # Implementation goes here
    return {
        "users": [],
        "count": 0,
        "success": True
    }
