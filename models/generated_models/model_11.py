"""
Auto-generated Pydantic Models
File: model_11.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class Tokenizer_porterInput(BaseModel):
    text: Any

class Tokenizer_porterOutput(BaseModel):
    result: Optional[Any] = None