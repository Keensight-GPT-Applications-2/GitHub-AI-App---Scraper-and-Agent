"""
Auto-generated Pydantic Model: extractauthorswithtimestamp
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ExtractauthorswithtimestampInput(BaseModel):
    fromFile: str
    toFile: str

class ExtractauthorswithtimestampOutput(BaseModel):
    result: Optional[Any] = None