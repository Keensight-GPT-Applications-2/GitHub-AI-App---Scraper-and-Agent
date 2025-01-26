"""
Auto-generated Pydantic Models
File: model_23.py
"""
from pydantic import BaseModel
from typing import Any, Optional


class ExtractalldataforcommonauthorsInput(BaseModel):
    postsFilename: Any  # Default type is 'Any'
    commonAuthorsFilename: Any  # Default type is 'Any'
    commonPostsFilename: Any  # Default type is 'Any'

class ExtractalldataforcommonauthorsOutput(BaseModel):
    result: Optional[Any] = None  # Return type inferred or defaulted