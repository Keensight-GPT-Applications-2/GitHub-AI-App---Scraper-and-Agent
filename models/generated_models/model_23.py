"""
Auto-generated Pydantic Models
File: model_23.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class ExtractalldataforcommonauthorsInput(BaseModel):
    postsFilename: Any
    commonAuthorsFilename: Any
    commonPostsFilename: Any

class ExtractalldataforcommonauthorsOutput(BaseModel):
    result: Optional[Any] = None