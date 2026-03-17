import os
import uuid
import secrets
from datetime import datetime, timedelta, timezone

import jwt
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from sweater.database import get_pool
from sweater.email_sender import send_confirmation_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


# ── Schemas ──────────────────────────────────────────────────────────

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

class ConfirmEmailRequest(BaseModel):
    token: str


# ── Helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ── Dependency: get current user from Authorization header ───────────

from fastapi import Request

async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1]
    payload = decode_jwt(token)
    return {"id": payload["sub"], "email": payload["email"]}


# ── Routes ───────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    pool = await get_pool()

    existing = await pool.fetchrow("SELECT id FROM users WHERE email = $1", body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    pw_hash = hash_password(body.password)
    row = await pool.fetchrow(
        "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id",
        body.email, pw_hash,
    )
    user_id = row["id"]

    # Create confirmation token
    token = secrets.token_urlsafe(48)
    await pool.execute(
        "INSERT INTO email_confirmations (user_id, token, expires_at) VALUES ($1, $2, $3)",
        user_id, token, datetime.now(timezone.utc) + timedelta(hours=24),
    )

    confirm_url = f"{FRONTEND_URL}/confirm-email?token={token}"
    await send_confirmation_email(body.email, confirm_url)

    return {"message": "Registration successful. Please check your email to confirm your account."}


@router.post("/confirm-email")
async def confirm_email(body: ConfirmEmailRequest):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT user_id, expires_at FROM email_confirmations WHERE token = $1",
        body.token,
    )
    if not row:
        raise HTTPException(status_code=400, detail="Invalid confirmation token")
    if row["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Confirmation token has expired")

    await pool.execute("UPDATE users SET is_confirmed = TRUE WHERE id = $1", row["user_id"])
    await pool.execute("DELETE FROM email_confirmations WHERE token = $1", body.token)

    return {"message": "Email confirmed successfully. You can now log in."}


@router.post("/login")
async def login(body: LoginRequest):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id, email, password_hash, is_confirmed FROM users WHERE email = $1",
        body.email,
    )
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not row["is_confirmed"]:
        raise HTTPException(status_code=403, detail="Please confirm your email before logging in")

    token = create_jwt(str(row["id"]), row["email"])
    return {"token": token, "user": {"id": str(row["id"]), "email": row["email"]}}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT id FROM users WHERE email = $1", body.email)

    # Always return success to avoid leaking whether email exists
    if row:
        token = secrets.token_urlsafe(48)
        # Remove any existing reset tokens for this user
        await pool.execute("DELETE FROM password_resets WHERE user_id = $1", row["id"])
        await pool.execute(
            "INSERT INTO password_resets (user_id, token, expires_at) VALUES ($1, $2, $3)",
            row["id"], token, datetime.now(timezone.utc) + timedelta(hours=1),
        )
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        await send_password_reset_email(body.email, reset_url)

    return {"message": "If that email is registered, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT user_id, expires_at FROM password_resets WHERE token = $1",
        body.token,
    )
    if not row:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if row["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    pw_hash = hash_password(body.password)
    await pool.execute("UPDATE users SET password_hash = $1 WHERE id = $2", pw_hash, row["user_id"])
    await pool.execute("DELETE FROM password_resets WHERE token = $1", body.token)

    return {"message": "Password reset successfully. You can now log in."}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"]}
