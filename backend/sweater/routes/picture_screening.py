import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sweater.database.references_db import get_reference_db
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles
from sweater.services.picture.picture_verification_service import (
    getUnverifiedPictureById,
    getUnverifiedPictures,
    verifyPicture,
    unverifyPicture,
    get_pictures_for_process,
    verify_picture_for_process,
)
from sweater.services.process.process_instance_service import get_process_instance_by_id
from sweater.services.process.attributes_service import get_process_attributes_by_process_id
from sweater.services.process.reference_service import get_reference_type_name_by_id, get_references_by_type_
from sweater.models.process_settings.Picture_processing_model import ProcessSettings

router = APIRouter(prefix="/pictures", tags=["pictures"])
from sweater.schemas.picture.picture_verification_scheme import VerifyRequest

# ── Process-based routes ─────────────────────────────────────────

@router.get("/process/{process_id}/settings")
async def get_process_screening_settings(
    process_id: str,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    # Find ProcessSettings entries linked to this process's type
    settings_rows = (
        db.query(ProcessSettings)
        .filter(ProcessSettings.type == process.type_id)
        .first()
    )

    # Collect all attributes from all matching process settings
    all_attributes = []
    if settings_rows:
        attrs = get_process_attributes_by_process_id(db, str(settings_rows.id))
        all_attributes.extend(attrs)

    result = []
    for attr in all_attributes:
        attr_data = {
            "id": str(attr.id),
            "title": attr.title,
            "is_shown": attr.is_shown,
            "is_editable": attr.is_editable,
            "reference_type_id": str(attr.reference_type_id) if attr.reference_type_id else None,
            "reference_type_name": None,
            "reference_values": [],
        }
        if attr.reference_type_id:
            refs = get_references_by_type_(db, str(attr.reference_type_id))
            attr_data["reference_values"] = [
                {"id": str(r.id), "value": r.reference_value}
                for r in refs
            ]
            attr_data["reference_type_name"] = get_reference_type_name_by_id(db, str(attr.reference_type_id))   
        result.append(attr_data)


    print(result)  # Debug log
    return result


@router.get("/process/{process_id}")
async def get_process_pictures(
    process_id: str,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    pictures = get_pictures_for_process(db, process_id)
    return pictures


@router.post("/process/verify")
async def verify_process_picture(
    body: VerifyRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    result = verify_picture_for_process(
        db,
        process_id=body.process_id,
        picture_id=body.id,
        url=body.url,
        extra=body.extra,
        user_id=user["user_id"],
    )
    return result


# ── Legacy routes ────────────────────────────────────────────────

@router.get("/{role}")
async def get_unverified_pictures(
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
    role: str = None
):
    pictures = getUnverifiedPictures(db)
    return pictures


@router.post("/verify")
async def verify_picture(
    body: VerifyRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    picture_id = body.id
    picture = getUnverifiedPictureById(db, picture_id)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    
    for key, value in body.extra.items():
        if hasattr(picture, key):
            setattr(picture, key, value)

    verifyPicture(db, picture)
    
    return {"ok": True}

@router.post("/unverify")
async def unverify_picture(
    body: VerifyRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    picture_id = body.id
    picture = getUnverifiedPictureById(db, picture_id)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    
    for key, value in body.extra.items():
        if hasattr(picture, key):
            setattr(picture, key, value)

    unverifyPicture(db, picture)
    
    return {"ok": True}
