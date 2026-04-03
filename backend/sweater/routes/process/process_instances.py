from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sweater.database.references_db import get_reference_db
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles
from sweater.schemas.process.process_instance_schema import CreateLinkProcess, UpdateProcessInstance
from sweater.services.process.process_instance_service import (
    list_process_instances,
    create_process_instance,
    update_process_status,
    get_process_instance_by_id,
)

router = APIRouter(prefix="/process-instances", tags=["process_instances"])


@router.get("/list")
async def get_process_list(
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    return list_process_instances(db)


@router.post("/create-link")
async def create_link_process(
    body: CreateLinkProcess,
    user: dict = Depends(require_roles("admin", "marketing_specialist")),
    db: Session = Depends(get_reference_db),
):
    process = create_process_instance(
        db,
        type_name="link",
        comment=body.link,
        initiator_id=user["user_id"],
    )
    return {
        "ok": True,
        "process_id": str(process.id),
    }


@router.put("/update/{process_id}")
async def update_process(
    process_id: str,
    body: UpdateProcessInstance,
    user: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    if body.status:
        updated = update_process_status(db, process_id, body.status)
        if not updated:
            raise HTTPException(status_code=400, detail="Invalid status")

    if body.comment is not None:
        process.comment = body.comment
        db.commit()

    return {"ok": True}
