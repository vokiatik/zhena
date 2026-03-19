from pydantic import BaseModel

class EmailConfirmationRequest(BaseModel):
    user_id: str
    token: str
    expires_at: str

class EmailConfirmationResponse(BaseModel):
    id: str
    user_id: str
    token: str
    expires_at: str
    created_at: str

    class Config:
        from_attributes = True

class ConfirmEmailRequest(BaseModel):
    token: str