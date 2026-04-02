from pydantic import BaseModel
from typing import Optional

class CreateProcess(BaseModel):
    title: str
    description: str
    table_name: str = "retail"

class UpdateProcess(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    table_name: Optional[str] = None