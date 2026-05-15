from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles
from sweater.services.picture.picture_verification_service import (
    get_pictures_for_process,
    verify_picture_for_process,
    decline_picture_for_process,
)
from sweater.services.picture.advertisement_screening_service import (
    get_advertisement_pictures_for_process,
    verify_advertisement,
    decline_advertisement,
)
from sweater.services.process.process_instance_service import (
    get_process_instance_by_id,
    get_process_type_name,
)
from sweater.services.process.attributes_service import get_process_attributes_by_process_id
from sweater.services.process.reference_service import get_reference_type_name_by_id, get_references_by_type_
from sweater.models.process_settings.Picture_processing_model import ProcessSettings
from sweater.schemas.picture.picture_verification_scheme import VerifyRequest, DeclineRequest
from pydantic import BaseModel

router = APIRouter(prefix="/pictures", tags=["pictures"])


class AdvertisementVerifyRequest(BaseModel):
    id: str
    process_id: str
    brand_id: Optional[str] = None
    brand_range_ids: Optional[List[str]] = None
    product_category_id: Optional[str] = None
    product_category_range_ids: Optional[List[str]] = None
    brand_category_id: Optional[str] = None
    advertising_category_ids: Optional[List[str]] = None
    incorrect_link_ids: Optional[List[str]] = None


class AdvertisementDeclineRequest(BaseModel):
    id: str
    process_id: str

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
            "is_nullable": attr.is_nullable,
            "reference_type_id": str(attr.reference_type_id) if attr.reference_type_id else None,
            "reference_type_name": None,
            "reference_values": [],
            "input_type": attr.input_type if attr.input_type else "text",
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
    process = get_process_instance_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    type_name = get_process_type_name(db, process)
    if type_name == "data_prep":
        return get_advertisement_pictures_for_process(db, process_id)
    return get_pictures_for_process(db, process_id)


@router.post("/process/advertisement/verify")
async def verify_advertisement_picture(
    body: AdvertisementVerifyRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    return verify_advertisement(
        db,
        process_id=body.process_id,
        ad_id=body.id,
        brand_id=body.brand_id,
        brand_range_ids=body.brand_range_ids or [],
        product_category_id=body.product_category_id,
        product_category_range_ids=body.product_category_range_ids or [],
        brand_category_id=body.brand_category_id,
        advertising_category_ids=body.advertising_category_ids or [],
        incorrect_link_ids=body.incorrect_link_ids,
    )


@router.post("/process/advertisement/decline")
async def decline_advertisement_picture(
    body: AdvertisementDeclineRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    return decline_advertisement(db, process_id=body.process_id, ad_id=body.id)


@router.post("/process/verify")
async def verify_process_picture(
    body: VerifyRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    return verify_picture_for_process(
        db,
        process_id=body.process_id,
        picture_id=body.id,
        url=body.url,
        extra=body.extra,
        user_id=user["id"],
    )


@router.post("/process/decline")
async def decline_process_picture(
    body: DeclineRequest,
    user: dict = Depends(require_roles("admin", "marketing_specialist", "analyst")),
    db: Session = Depends(get_reference_db),
):
    return decline_picture_for_process(
        db,
        process_id=body.process_id,
        picture_id=body.id,
    )
