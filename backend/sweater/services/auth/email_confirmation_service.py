from sqlalchemy.orm import Session
from sweater.schemas.auth.Email_confirmation_schema import EmailConfirmationRequest, EmailConfirmationResponse
from sweater.models.Email_confirmations_model import EmailConfirmation

def create_email_confirmation(db: Session, email_confirmation: EmailConfirmationRequest):
    db_email_confirmation = EmailConfirmation(
        user_id=email_confirmation.user_id,
        token=email_confirmation.token,
        expires_at=email_confirmation.expires_at
    )
    db.add(db_email_confirmation)
    db.commit()
    db.refresh(db_email_confirmation)
    return db_email_confirmation

def get_email_confirmation_by_token(db: Session, token: str):
    return db.query(EmailConfirmation).filter(EmailConfirmation.token == token).first()

def delete_email_confirmation_by_token(db: Session, token: str):
    email_confirmation = db.query(EmailConfirmation).filter(EmailConfirmation.token == token).first()
    if email_confirmation:
        db.delete(email_confirmation)
        db.commit()
        return True
    return False