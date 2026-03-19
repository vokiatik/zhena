from pydantic import BaseModel

class ProcessingStatus(BaseModel):
    message_id: str
    status: str | None = None
    label: str | None = None
    created_at: str