from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: str
    password_hash: str


class UserUpdate(BaseModel):
    email: str | None = None
    is_confirmed: bool | None = None
    password_hash: str | None = None

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str