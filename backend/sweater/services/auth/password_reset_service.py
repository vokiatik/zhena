from sqlalchemy.orm import Session
from sweater.schemas.auth.Password_reset_schema import PasswordResetRequest
from sweater.models.Password_reset_model import PasswordReset

def create_password_reset(db: Session, password_reset: PasswordResetRequest):
    db_password_reset = PasswordReset(
        user_id=password_reset.user_id,
        token=password_reset.token,
        expires_at=password_reset.expires_at
    )
    db.add(db_password_reset)
    db.commit()
    db.refresh(db_password_reset)
    return db_password_reset

def get_password_reset_by_token(db: Session, token: str):
    return db.query(PasswordReset).filter(PasswordReset.token == token).first()

def delete_password_reset_by_token(db: Session, token: str):
    password_reset = db.query(PasswordReset).filter(PasswordReset.token == token).first()
    if password_reset:
        db.delete(password_reset)
        db.commit()
        return True
    return False

def delete_password_resets_by_user_id(db: Session, user_id: int):
    password_resets = db.query(PasswordReset).filter(PasswordReset.user_id == user_id).all()
    for reset in password_resets:
        db.delete(reset)
    db.commit()
    return True