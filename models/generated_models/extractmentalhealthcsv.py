"""
Auto-generated Pydantic Model: extractmentalhealthcsv
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ExtractmentalhealthcsvInput(BaseModel):
    start: int
    end: int

class ExtractmentalhealthcsvOutput(BaseModel):
    result: Optional[Any] = None