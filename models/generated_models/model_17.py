"""
Auto-generated Pydantic Models
File: model_17.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class WordcloudInput(BaseModel):
    self: Any
    filename: Any

class WordcloudOutput(BaseModel):
    result: Optional[Any] = None