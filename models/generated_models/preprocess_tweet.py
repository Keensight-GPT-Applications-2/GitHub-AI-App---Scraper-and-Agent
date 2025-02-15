"""
Auto-generated Pydantic Model: preprocess_tweet
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class Preprocess_tweetInput(BaseModel):
    text: str

class Preprocess_tweetOutput(BaseModel):
    result: Optional[Any] = None