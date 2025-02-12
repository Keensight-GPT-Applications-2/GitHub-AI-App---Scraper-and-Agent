"""
Auto-generated Pydantic Models
File: model_19.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class ExtractsuicidalwatchInput(BaseModel):
    self: Any
    reddit: Any

class ExtractsuicidalwatchOutput(BaseModel):
    result: Optional[Any] = None