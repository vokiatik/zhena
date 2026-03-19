from pydantic import BaseModel

class MessageRequest(BaseModel):
    chat_id: str
    user_id: str
    message: str
    timestamp: str
