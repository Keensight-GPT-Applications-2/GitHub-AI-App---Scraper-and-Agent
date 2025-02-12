"""
Auto-generated Pydantic Models
File: model_18.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class Wordcloud2Input(BaseModel):
    self: Any
    filename: Any

class Wordcloud2Output(BaseModel):
    result: Optional[Any] = None