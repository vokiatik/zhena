import uuid
from sqlalchemy.orm import Session
from sweater.models.auth.Role_model import RoleModel, UserRoleModel


def get_all_roles(db: Session):
    return db.query(RoleModel).all()


def get_role_by_name(db: Session, name: str):
    return db.query(RoleModel).filter(RoleModel.name == name).first()


def get_role_by_id(db: Session, role_id: uuid.UUID):
    return db.query(RoleModel).filter(RoleModel.id == role_id).first()


def create_role(db: Session, name: str):
    role = RoleModel(name=name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: uuid.UUID):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        return None
    db.delete(role)
    db.commit()
    return role


def get_user_roles(db: Session, user_id: uuid.UUID) -> list[str]:
    rows = (
        db.query(RoleModel.name)
        .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
        .filter(UserRoleModel.user_id == user_id)
        .all()
    )
    return [r[0] for r in rows]


def assign_role_to_user(db: Session, user_id: uuid.UUID, role_id: uuid.UUID):
    existing = (
        db.query(UserRoleModel)
        .filter(UserRoleModel.user_id == user_id, UserRoleModel.role_id == role_id)
        .first()
    )
    if existing:
        return existing
    user_role = UserRoleModel(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role


def remove_role_from_user(db: Session, user_id: uuid.UUID, role_id: uuid.UUID):
    user_role = (
        db.query(UserRoleModel)
        .filter(UserRoleModel.user_id == user_id, UserRoleModel.role_id == role_id)
        .first()
    )
    if not user_role:
        return None
    db.delete(user_role)
    db.commit()
    return user_role


def seed_default_roles(db: Session):
    """Insert the three default roles if they don't exist yet."""
    for name in ("admin", "analyst", "marketing_specialist"):
        if not get_role_by_name(db, name):
            create_role(db, name)
