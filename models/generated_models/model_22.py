"""
Auto-generated Pydantic Models
File: model_22.py
"""
from pydantic import BaseModel
from typing import Any, Optional

class ExtractmhandswcommonauthorsInput(BaseModel):
    generalIssuesFilename: Any
    suicideWatchFilename: Any
    commonAuthorsFilename: Any

class ExtractmhandswcommonauthorsOutput(BaseModel):
    result: Optional[Any] = None