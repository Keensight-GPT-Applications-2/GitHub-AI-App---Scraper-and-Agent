"""
Auto-generated Pydantic Model: preprocess_text
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class Preprocess_textInput(BaseModel):
    sen: str

class Preprocess_textOutput(BaseModel):
    result: Optional[Any] = None