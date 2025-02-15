"""
Auto-generated Pydantic Model: tokenizer_porter
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class Tokenizer_porterInput(BaseModel):
    text: str

class Tokenizer_porterOutput(BaseModel):
    result: Optional[Any] = None