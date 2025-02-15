"""
Auto-generated Pydantic Model: extractsuicidalwatch
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ExtractsuicidalwatchInput(BaseModel):
    reddit: Dict[str, Any]

class ExtractsuicidalwatchOutput(BaseModel):
    result: Optional[Any] = None