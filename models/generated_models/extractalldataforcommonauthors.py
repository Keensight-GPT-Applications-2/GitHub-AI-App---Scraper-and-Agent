"""
Auto-generated Pydantic Model: extractalldataforcommonauthors
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ExtractalldataforcommonauthorsInput(BaseModel):
    postsFilename: str
    commonAuthorsFilename: str
    commonPostsFilename: str

class ExtractalldataforcommonauthorsOutput(BaseModel):
    result: Optional[Any] = None