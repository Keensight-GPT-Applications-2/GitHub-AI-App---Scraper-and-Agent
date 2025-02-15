"""
Auto-generated Pydantic Model: wordcloud2
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class Wordcloud2Input(BaseModel):
    filename: str

class Wordcloud2Output(BaseModel):
    result: Optional[Any] = None