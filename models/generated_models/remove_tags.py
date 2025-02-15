"""
Auto-generated Pydantic Model: remove_tags
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class Remove_tagsInput(BaseModel):
    text: str

class Remove_tagsOutput(BaseModel):
    result: Optional[Any] = None