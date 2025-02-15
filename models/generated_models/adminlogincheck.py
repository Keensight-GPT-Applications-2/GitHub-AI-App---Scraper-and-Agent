"""
Auto-generated Pydantic Model: adminlogincheck
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class AdminlogincheckInput(BaseModel):
    request: Dict[str, Any]

class AdminlogincheckOutput(BaseModel):
    result: Optional[Any] = None