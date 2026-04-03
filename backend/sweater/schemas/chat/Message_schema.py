from pydantic import BaseModel

class MessageRequest(BaseModel):
    chat_id: str
    role: str
    content: str
