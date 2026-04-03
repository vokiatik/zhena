from pydantic import BaseModel
from typing import Optional

class CreateProcess(BaseModel):
    title: str
    description: str
    type: Optional[str] = None

class UpdateProcess(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None