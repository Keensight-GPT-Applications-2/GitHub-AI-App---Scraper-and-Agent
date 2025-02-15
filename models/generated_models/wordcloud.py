"""
Auto-generated Pydantic Model: wordcloud
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class WordcloudInput(BaseModel):
    filename: str

class WordcloudOutput(BaseModel):
    result: Optional[Any] = None