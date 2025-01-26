"""
Auto-generated Pydantic Models
File: model_18.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class Wordcloud2Input(BaseModel):
    self: Any  # Default type is 'Any'
    filename: Any  # Default type is 'Any'

class Wordcloud2Output(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted