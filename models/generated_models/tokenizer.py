"""
Auto-generated Pydantic Model: tokenizer
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class TokenizerInput(BaseModel):
    text: str

class TokenizerOutput(BaseModel):
    result: Optional[Any] = None