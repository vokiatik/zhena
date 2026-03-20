import uuid

from sqlalchemy.orm import Session
from sweater.schemas.auth.User_schema import UserCreate, UserUpdate
from sweater.models.User_model import UserModel

# ✅ CREATE (INSERT)
def create_user(db: Session, user: UserCreate):
    db_user = UserModel(
        email=user.email,
        password_hash=user.password_hash,
        is_confirmed=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ✅ READ (SELECT ONE)
def get_user(db: Session, user_id: uuid.UUID):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

# ✅ READ (SELECT MANY)
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserModel).offset(skip).limit(limit).all()


# ✅ UPDATE
def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not db_user:
        return None

    if user_update.email is not None:
        db_user.email = user_update.email

    if user_update.is_confirmed is not None:
        db_user.is_confirmed = user_update.is_confirmed

    if user_update.password_hash is not None:
        db_user.password_hash = user_update.password_hash

    db.commit()
    db.refresh(db_user)
    return db_user


# ✅ DELETE
def delete_user(db: Session, user_id: uuid.UUID):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user