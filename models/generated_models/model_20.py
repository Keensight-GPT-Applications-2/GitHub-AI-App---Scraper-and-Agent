"""
Auto-generated Pydantic Models
File: model_20.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class ExtractmentalhealthcsvInput(BaseModel):
    self: Any
    start: Any
    end: Any

class ExtractmentalhealthcsvOutput(BaseModel):
    result: Optional[Any] = None