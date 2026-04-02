from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sweater.database.base_db import get_db
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles
from sweater.schemas.auth.Role_schema import AssignRoleRequest, RemoveRoleRequest
from sweater.services.auth.role_service import (
    get_all_roles,
    get_role_by_name,
    get_user_roles,
    assign_role_to_user,
    remove_role_from_user,
    seed_default_roles,
)
from sweater.services.auth.user_service import get_user, get_users

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/list")
async def list_roles(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roles = get_all_roles(db)
    return [{"id": str(r.id), "name": r.name} for r in roles]


@router.get("/my")
async def my_roles(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roles = get_user_roles(db, user["id"])
    return {"roles": roles}


@router.get("/user/{user_id}")
async def user_roles(
    user_id: str,
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    roles = get_user_roles(db, user_id)
    return {"user_id": user_id, "roles": roles}


@router.post("/assign")
async def assign_role(
    body: AssignRoleRequest,
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    role = get_role_by_name(db, body.role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    target_user = get_user(db, body.user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    assign_role_to_user(db, body.user_id, role.id)
    return {"message": f"Role '{body.role_name}' assigned to user"}


@router.post("/remove")
async def remove_role(
    body: RemoveRoleRequest,
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    role = get_role_by_name(db, body.role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    result = remove_role_from_user(db, body.user_id, role.id)
    if not result:
        raise HTTPException(status_code=404, detail="User does not have this role")
    return {"message": f"Role '{body.role_name}' removed from user"}


@router.get("/users")
async def list_users_with_roles(
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    users = get_users(db, skip=0, limit=1000)
    result = []
    for u in users:
        roles = get_user_roles(db, u.id)
        result.append({
            "id": str(u.id),
            "email": u.email,
            "roles": roles,
        })
    return result


@router.post("/seed")
async def seed_roles(
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    seed_default_roles(db)
    return {"message": "Default roles seeded"}
