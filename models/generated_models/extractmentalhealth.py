"""
Auto-generated Pydantic Model: extractmentalhealth
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ExtractmentalhealthInput(BaseModel):
    reddit: Dict[str, Any]

class ExtractmentalhealthOutput(BaseModel):
    result: Optional[Any] = None