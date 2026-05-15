from sqlalchemy.orm import Session

from sweater.services.process.process_instance_service import (
    get_process_instance_by_id,
    get_process_status_name,
    update_process_status,
)
from sweater.services.picture.advertisement_screening_service import (
    get_advertisement_pictures_for_process,
    verify_advertisement,
    decline_advertisement,
)


def get_pictures_for_process(db: Session, process_id: str):
    return get_advertisement_pictures_for_process(db, process_id)


def verify_picture_for_process(
    db: Session,
    process_id: str,
    picture_id: str,
    url: str,
    extra: dict,
    user_id: str,
):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        return {"ok": False, "error": "Process not found"}

    status_name = get_process_status_name(db, process)
    if status_name == "initiated":
        update_process_status(db, process_id, "in progress")

    return verify_advertisement(
        db,
        process_id=process_id,
        ad_id=picture_id,
        brand_id=extra.get("brand_id"),
        brand_range_ids=extra.get("brand_range_ids") or [],
        product_category_id=extra.get("product_category_id"),
        product_category_range_ids=extra.get("product_category_range_ids") or [],
        brand_category_id=extra.get("brand_category_id"),
        advertising_category_ids=extra.get("advertising_category_ids") or [],
    )


def decline_picture_for_process(db: Session, process_id: str, picture_id: str):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        return {"ok": False, "error": "Process not found"}

    status_name = get_process_status_name(db, process)
    if status_name == "initiated":
        update_process_status(db, process_id, "in progress")

    return decline_advertisement(db, process_id=process_id, ad_id=picture_id)
