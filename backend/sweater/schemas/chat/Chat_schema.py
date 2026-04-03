from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    title: str

