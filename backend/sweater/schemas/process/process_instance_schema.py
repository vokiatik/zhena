from pydantic import BaseModel
from typing import Optional


class CreateLinkProcess(BaseModel):
    link: str


class UpdateProcessInstance(BaseModel):
    status: Optional[str] = None
    comment: Optional[str] = None


class ProcessInstanceResponse(BaseModel):
    id: str
    type_name: str
    status_name: str
    comment: Optional[str] = None
    initiator_id: Optional[str] = None
    total_items: Optional[int] = None
    parent_process_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
