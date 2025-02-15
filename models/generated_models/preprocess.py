"""
Auto-generated Pydantic Model: preprocess
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class PreprocessInput(BaseModel):
    tweet: str

class PreprocessOutput(BaseModel):
    result: Optional[Any] = None