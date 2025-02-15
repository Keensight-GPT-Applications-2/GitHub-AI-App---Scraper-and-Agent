"""
Auto-generated Pydantic Model: extractmhandswcommonauthors
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict

class ExtractmhandswcommonauthorsInput(BaseModel):
    generalIssuesFilename: str
    suicideWatchFilename: str
    commonAuthorsFilename: str

class ExtractmhandswcommonauthorsOutput(BaseModel):
    result: Optional[Any] = None