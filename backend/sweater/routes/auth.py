import os
import secrets
import uuid
import jwt
import bcrypt

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Session

from sweater.schemas.auth.Password_reset_schema import PasswordResetRequest
from sweater.database.base_db import get_db
from sweater.schemas.auth.User_schema import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, UserCreate, UserUpdate
from sweater.schemas.auth.Email_confirmation_schema import ConfirmEmailRequest, EmailConfirmationRequest
from sweater.services.auth.email_confirmation_service import create_email_confirmation, delete_email_confirmation_by_token, get_email_confirmation_by_token
from sweater.services.auth.password_reset_service import create_password_reset, delete_password_reset_by_token, delete_password_resets_by_user_id, get_password_reset_by_token
from sweater.services.auth.user_service import create_user, get_user_by_email, update_user
from sweater.email_sender import send_confirmation_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

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

async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1]
    payload = decode_jwt(token)
    return {"id": payload["sub"], "email": payload["email"]}


# ── Routes ───────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
async def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    user = get_user_by_email(db, body.email)
    if user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    pw_hash = hash_password(body.password)

    db_user = create_user(db, UserCreate(email=body.email, password_hash=pw_hash))

    user_id = db_user.id

    # Create confirmation token
    token = secrets.token_urlsafe(48)
    
    create_email_confirmation(db, EmailConfirmationRequest(
        user_id=str(user_id),
        token=token,
        expires_at=(datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    ))
    
    confirm_url = f"{FRONTEND_URL}/confirm-email?token={token}"
    await send_confirmation_email(body.email, confirm_url)

    return {"message": "Registration successful. Please check your email to     confirm your account."}


@router.post("/confirm-email")
async def confirm_email(
    body: ConfirmEmailRequest,
    db: Session = Depends(get_db),
):
    email_confirmation = get_email_confirmation_by_token(db, body.token)
    if not email_confirmation:
        raise HTTPException(status_code=400, detail="Invalid confirmation token")
    if email_confirmation.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Confirmation token has expired")
    
    update_user(db, email_confirmation.user_id, UserUpdate(is_confirmed=True))
    delete_email_confirmation_by_token(db, body.token)

    return {"message": "Email confirmed successfully. You can now log in."}


@router.post("/login")
async def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, body.email)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_confirmed:
        raise HTTPException(status_code=403, detail="Please confirm your email before logging in")

    token = create_jwt(str(user.id), user.email)
    return {"token": token, "user": {"id": str(user.id), "email": user.email}}


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, body.email)

    if user:
        token = secrets.token_urlsafe(48)
        # Remove any existing reset tokens for this user
        delete_password_resets_by_user_id(db, user.id)
        password_reset = PasswordResetRequest(
            user_id=str(user.id),
            token=token,
            expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        )
        create_password_reset(db, password_reset)
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        await send_password_reset_email(body.email, reset_url)
    
    return {"message": "If that email is registered, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    password_reset = get_password_reset_by_token(db, body.token)
    if not password_reset:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    if password_reset.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    pw_hash = hash_password(body.password)
    update_user(db, password_reset.user_id, UserUpdate(password_hash=pw_hash))
    delete_password_reset_by_token(db, body.token)

    return {"message": "Password reset successfully. You can now log in."}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"]}
