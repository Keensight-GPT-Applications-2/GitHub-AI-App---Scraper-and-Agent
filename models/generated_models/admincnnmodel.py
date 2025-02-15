"""
Auto-generated Pydantic Model: admincnnmodel
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class AdmincnnmodelInput(BaseModel):
    request: Dict[str, Any]

class AdmincnnmodelOutput(BaseModel):
    result: Optional[Any] = None