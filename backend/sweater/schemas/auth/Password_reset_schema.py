from pydantic import BaseModel

class PasswordResetRequest(BaseModel):
    user_id: str
    token: str
    expires_at: str

class PasswordResetResponse(BaseModel):
    id: str
    user_id: str
    token: str
    expires_at: str
    created_at: str

    class Config:
        from_attributes = True