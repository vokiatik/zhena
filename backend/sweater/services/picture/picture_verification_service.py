import uuid
from sqlalchemy.orm import Session

from sweater.models.retail.Retail_model import Retail
from sweater.models.retail.Retail_processed_model import RetailProcessed
from sweater.models.retail.Analyst_processed_model import AnalystProcessed
from sweater.models.process_settings.Process_model import Process
from sweater.services.process.process_instance_service import (
    get_process_instance_by_id,
    get_process_type_name,
    get_process_status_name,
    update_process_status,
    set_process_total_items,
    create_process_instance,
)
from sweater.services.picture.cloud_service import list_cloud_pictures


# ── File type ────────────────────────────────────────────────────

def get_pictures_for_file_process(db: Session, process: Process):
    """Get unverified retail rows for a file process."""
    rows = (
        db.query(Retail)
        .filter(Retail.process_id == process.id, Retail.verified == False)
        .order_by(Retail.created_at)
        .all()
    )
    set_process_total_items(
        db, str(process.id),
        db.query(Retail).filter(Retail.process_id == process.id).count()
    )
    result = []
    for r in rows:
        result.append({
            "id": str(r.id),
            "advertisement_id": r.advertisement_id or "",
            "retailer_clean": r.retailer_clean or "",
            "advertiser_producer": r.advertiser_producer or "",
            "brands_list": r.brands_list or "",
            "brands_list_clean": r.brands_list_clean or "",
            "ferrero_category": r.ferrero_category or "",
            "ferrero_category_range": r.ferrero_category_range or "",
            "ferrero_category_multibrand": r.ferrero_category_multibrand or "",
            "first_screen_date": str(r.first_screen_date) if r.first_screen_date else "",
            "last_screen_date": str(r.last_screen_date) if r.last_screen_date else "",
            "verified": r.verified,
        })
    return result


def verify_file_picture(db: Session, process: Process, picture_id: str, extra: dict, user_id: str):
    """Verify a picture for file-type process."""
    retail_row = db.query(Retail).filter(Retail.id == picture_id).first()
    if not retail_row:
        return None

    # Update retail fields
    for key, value in extra.items():
        if hasattr(retail_row, key):
            setattr(retail_row, key, value)
    retail_row.verified = True

    # Insert into retail_processed
    processed = RetailProcessed(
        retailer_clean=extra.get("retailer_clean", retail_row.retailer_clean),
        advertiser_producer=extra.get("advertiser_producer", retail_row.advertiser_producer),
        brands_list=extra.get("brands_list", retail_row.brands_list),
        brands_list_clean=extra.get("brands_list_clean", retail_row.brands_list_clean),
        ferrero_category=extra.get("ferrero_category", retail_row.ferrero_category),
        ferrero_category_range=extra.get("ferrero_category_range", retail_row.ferrero_category_range),
        ferrero_category_multibrand=extra.get("ferrero_category_multibrand", retail_row.ferrero_category_multibrand),
        first_screen_date=retail_row.first_screen_date,
        last_screen_date=retail_row.last_screen_date,
        advertisement_id=extra.get("advertisement_id", retail_row.advertisement_id),
        user_id=user_id,
        type="file",
        process_id=process.id,
    )
    db.add(processed)
    db.commit()

    # Check completion
    remaining = db.query(Retail).filter(
        Retail.process_id == process.id, Retail.verified == False
    ).count()
    return remaining


# ── Link type ────────────────────────────────────────────────────

def get_pictures_for_link_process(db: Session, process: Process):
    """Get unverified pictures from cloud folder for a link process."""
    folder_url = process.comment or ""
    all_pictures = list_cloud_pictures(folder_url)

    # Exclude already processed pictures
    already_processed = (
        db.query(RetailProcessed.advertisement_id)
        .filter(RetailProcessed.process_id == process.id)
        .all()
    )
    processed_links = {r[0] for r in already_processed}

    remaining = [url for url in all_pictures if url not in processed_links]

    total = len(all_pictures)
    set_process_total_items(db, str(process.id), total)

    result = []
    for i, url in enumerate(remaining):
        result.append({
            "id": f"link-{i}-{uuid.uuid4().hex[:8]}",
            "advertisement_id": url,
            "retailer_clean": "",
            "advertiser_producer": "",
            "brands_list": "",
            "brands_list_clean": "",
            "ferrero_category": "",
            "ferrero_category_range": "",
            "ferrero_category_multibrand": "",
            "first_screen_date": "",
            "last_screen_date": "",
            "verified": False,
        })
    return result


def verify_link_picture(db: Session, process: Process, url: str, extra: dict, user_id: str):
    """Verify a picture for link-type process."""
    processed = RetailProcessed(
        retailer_clean=extra.get("retailer_clean", ""),
        advertiser_producer=extra.get("advertiser_producer", ""),
        brands_list=extra.get("brands_list", ""),
        brands_list_clean=extra.get("brands_list_clean", ""),
        ferrero_category=extra.get("ferrero_category", ""),
        ferrero_category_range=extra.get("ferrero_category_range", ""),
        ferrero_category_multibrand=extra.get("ferrero_category_multibrand", ""),
        advertisement_id=url,
        user_id=user_id,
        type="link",
        process_id=process.id,
    )
    db.add(processed)
    db.commit()

    # Check completion
    processed_count = (
        db.query(RetailProcessed)
        .filter(RetailProcessed.process_id == process.id)
        .count()
    )
    total = process.total_items or 0
    remaining = max(0, total - processed_count)
    return remaining


# ── Analyst type ─────────────────────────────────────────────────

def get_pictures_for_analyst_process(db: Session, process: Process):
    """Get unprocessed pictures for analyst-type process."""
    parent_process_id = process.parent_process_id
    if not parent_process_id:
        return []

    # Get retail_processed rows from parent link process
    source_rows = (
        db.query(RetailProcessed)
        .filter(
            RetailProcessed.process_id == parent_process_id,
            RetailProcessed.type == "link",
        )
        .order_by(RetailProcessed.created_at)
        .all()
    )

    # Exclude already processed by this analyst process
    already_done = (
        db.query(AnalystProcessed.retail_processed_id)
        .filter(AnalystProcessed.process_id == process.id)
        .all()
    )
    done_ids = {str(r[0]) for r in already_done}

    total = len(source_rows)
    set_process_total_items(db, str(process.id), total)

    result = []
    for row in source_rows:
        if str(row.id) in done_ids:
            continue
        result.append({
            "id": str(row.id),
            "advertisement_id": row.advertisement_id or "",
            "format": "",
            "weekly_price": "",
            "verified": False,
        })
    return result


def verify_analyst_picture(db: Session, process: Process, retail_processed_id: str, extra: dict, user_id: str):
    """Verify a picture for analyst-type process."""
    source = db.query(RetailProcessed).filter(RetailProcessed.id == retail_processed_id).first()

    analyst = AnalystProcessed(
        format=extra.get("format", ""),
        weekly_price=extra.get("weekly_price", ""),
        user_id=user_id,
        process_id=process.id,
        retail_processed_id=retail_processed_id,
        link=source.advertisement_id if source else extra.get("advertisement_id", ""),
    )
    db.add(analyst)
    db.commit()

    # Check completion
    processed_count = (
        db.query(AnalystProcessed)
        .filter(AnalystProcessed.process_id == process.id)
        .count()
    )
    total = process.total_items or 0
    remaining = max(0, total - processed_count)
    return remaining


# ── Dispatch helpers ─────────────────────────────────────────────

def get_pictures_for_process(db: Session, process_id: str):
    """Get pictures for any process type."""
    process = get_process_instance_by_id(db, process_id)
    if not process:
        return []

    type_name = get_process_type_name(db, process)

    if type_name == "file":
        return get_pictures_for_file_process(db, process)
    elif type_name == "link":
        return get_pictures_for_link_process(db, process)
    elif type_name == "analyst":
        return get_pictures_for_analyst_process(db, process)
    return []


def verify_picture_for_process(db: Session, process_id: str, picture_id: str, url: str, extra: dict, user_id: str):
    """Verify a picture and handle status transitions."""
    process = get_process_instance_by_id(db, process_id)
    if not process:
        return {"ok": False, "error": "Process not found"}

    type_name = get_process_type_name(db, process)
    status_name = get_process_status_name(db, process)

    # Transition: initiated → in progress
    if status_name == "initiated":
        update_process_status(db, process_id, "in progress")

    # Verify based on type
    if type_name == "file":
        remaining = verify_file_picture(db, process, picture_id, extra, user_id)
    elif type_name == "link":
        remaining = verify_link_picture(db, process, url, extra, user_id)
    elif type_name == "analyst":
        remaining = verify_analyst_picture(db, process, picture_id, extra, user_id)
    else:
        return {"ok": False, "error": f"Unknown process type: {type_name}"}

    if remaining is None:
        return {"ok": False, "error": "Picture not found"}

    # Transition: in progress → done (when no remaining items)
    if remaining == 0:
        update_process_status(db, process_id, "done")

        # Auto-create analyst process when link process is done
        if type_name == "link":
            create_process_instance(
                db,
                type_name="analyst",
                comment=f"Auto-created from link process {process_id}",
                initiator_id=str(process.initiator_id) if process.initiator_id else None,
                parent_process_id=str(process.id),
            )

    return {"ok": True, "remaining": remaining}


# ── Legacy helpers (kept for backward compatibility) ─────────────

def getUnverifiedPictures(db: Session):
    return db.query(Retail).filter_by(verified=False).order_by(Retail.created_at).all()


def verifyPicture(db: Session, values: Retail):
    picture = db.query(Retail).filter_by(id=values.id).first()
    if picture:
        picture.retailer_clean = values.retailer_clean
        picture.advertiser_producer = values.advertiser_producer
        picture.brands_list = values.brands_list
        picture.brands_list_clean = values.brands_list_clean
        picture.ferrero_category = values.ferrero_category
        picture.ferrero_category_range = values.ferrero_category_range
        picture.ferrero_category_multibrand = values.ferrero_category_multibrand
        picture.first_screen_date = values.first_screen_date
        picture.last_screen_date = values.last_screen_date
        picture.advertisement_id = values.advertisement_id
        picture.verified = True
        db.commit()


def unverifyPicture(db: Session, values: Retail):
    picture = db.query(Retail).filter_by(id=values.id).first()
    if picture:
        picture.verified = False
        db.commit()


def getUnverifiedPictureById(db: Session, picture_id: str):
    return db.query(Retail).filter_by(id=picture_id).first()
