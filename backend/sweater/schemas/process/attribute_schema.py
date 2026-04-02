from pydantic import BaseModel
from typing import Optional

class CreateProcessAttribute(BaseModel):
    process_id: str
    title: str
    is_shown: bool = True
    is_editable: bool = True
    reference_type_id: Optional[str] = None

class UpdateProcessAttribute(BaseModel):
    id: str
    is_shown: Optional[bool] = None
    is_editable: Optional[bool] = None
    reference_type_id: Optional[str] = None