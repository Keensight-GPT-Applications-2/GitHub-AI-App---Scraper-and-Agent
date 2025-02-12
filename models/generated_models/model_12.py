"""
Auto-generated Pydantic Models
File: model_12.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class TokenizerInput(BaseModel):
    text: Any

class TokenizerOutput(BaseModel):
    result: Optional[Any] = None