"""
Auto-generated Pydantic Model: Adminactivausers
"""
from pydantic import BaseModel
from typing import Any, Optional, Dict
import json

class AdminactivausersInput(BaseModel):
    request: Dict[str, Any]

class AdminactivausersOutput(BaseModel):
    result: Optional[Any] = None

def AdminActivaUsers(request) -> Optional[Any]:
    """No docstring provided."""
    import json  # Ensure json is imported in each function
    return {'status': 'success', 'processed_data': json.dumps(request)}