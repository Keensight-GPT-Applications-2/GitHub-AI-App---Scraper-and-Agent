"""
Auto-generated Pydantic Models
File: model_8.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class PreprocessInput(BaseModel):
    self: Any
    tweet: Any

class PreprocessOutput(BaseModel):
    result: Optional[Any] = None