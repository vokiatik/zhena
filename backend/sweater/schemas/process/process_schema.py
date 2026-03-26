from pydantic import BaseModel

class UpdateProcess(BaseModel):
    id: str
    title: str
    description: str
    created_at: str
