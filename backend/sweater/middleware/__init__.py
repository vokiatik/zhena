"""
Role-based access control middleware for FastAPI routes.

Usage in routes:
    from sweater.middleware.role_middleware import require_roles

    @router.get("/admin-only", dependencies=[Depends(require_roles("admin"))])
    async def admin_endpoint():
        ...

    @router.get("/multi", dependencies=[Depends(require_roles("admin", "analyst"))])
    async def multi_role_endpoint():
        ...
"""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from sweater.database.base_db import get_db
from sweater.routes.auth import get_current_user
from sweater.services.auth.role_service import get_user_roles


def require_roles(*allowed_roles: str):
    """Return a FastAPI dependency that asserts the current user has ≥1 of the allowed roles."""

    async def _check(
        request: Request,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        user_roles = get_user_roles(db, user["id"])
        # admin always passes
        if "admin" in user_roles:
            return user
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return _check
