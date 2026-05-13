"""
Advertisement screening service.

Serves advertisement data (from the new tables) for analyst review within
a data_prep process, and handles verify / decline actions.
"""

import uuid
from typing import Optional
from sqlalchemy.orm import Session

from sweater.models.advertisement.Advertisement_model import Advertisement
from sweater.models.advertisement.Advertisement_link_model import AdvertisementLink
from sweater.models.advertisement.Advertisement_brand_model import AdvertisementBrand
from sweater.models.advertisement.Advertisement_category_model import AdvertisementCategory
from sweater.models.advertisement.Advertisement_add_category_model import AdvertisementAddCategory
from sweater.models.Dictionaries.simple_value import SimpleValue
from sweater.models.Dictionaries.simple_value_type import SimpleValueType
from sweater.services.process.process_instance_service import (
    get_process_instance_by_id,
    get_process_type_name,
    get_process_status_name,
    set_process_total_items,
    update_process_status,
)


# ---------------------------------------------------------------------------
# Helper: load all simple_value options grouped by field_name
# ---------------------------------------------------------------------------

def _load_options(db: Session) -> dict:
    """Return {field_name: [{id, value}, ...]} for the four editable fields."""
    target_fields = ("brand", "product_category", "brand_category", "add_category")
    options: dict = {f: [] for f in target_fields}

    svt_rows = (
        db.query(SimpleValueType)
        .filter(SimpleValueType.field_name.in_(target_fields))
        .all()
    )
    for svt in svt_rows:
        values = (
            db.query(SimpleValue)
            .filter(SimpleValue.column_name_id == svt.id)
            .order_by(SimpleValue.value)
            .all()
        )
        options[svt.field_name] = [{"id": str(v.id), "value": v.value} for v in values]

    return options


# ---------------------------------------------------------------------------
# Helper: serialise one Advertisement row with all related data
# ---------------------------------------------------------------------------

def _serialise_advertisement(db: Session, ad: Advertisement) -> dict:
    # Resolve single-FK fields via simple_value
    def _sv(sv_id: Optional[uuid.UUID]) -> Optional[dict]:
        if not sv_id:
            return None
        sv = db.query(SimpleValue).filter(SimpleValue.id == sv_id).first()
        return {"id": str(sv.id), "value": sv.value} if sv else None

    # Collect links
    links = (
        db.query(AdvertisementLink)
        .filter(AdvertisementLink.add_id == ad.id)
        .all()
    )
    first_url = links[0].link if links else ""

    # Brand range
    brand_range_rows = (
        db.query(AdvertisementBrand)
        .filter(AdvertisementBrand.add_id == ad.id)
        .all()
    )
    brand_range = []
    for br in brand_range_rows:
        sv = db.query(SimpleValue).filter(SimpleValue.id == br.brand_id).first()
        if sv:
            brand_range.append({"row_id": str(br.id), "id": str(sv.id), "value": sv.value})

    # Product category range
    cat_range_rows = (
        db.query(AdvertisementCategory)
        .filter(AdvertisementCategory.add_id == ad.id)
        .all()
    )
    product_category_range = []
    for cr in cat_range_rows:
        sv = db.query(SimpleValue).filter(SimpleValue.id == cr.category_id).first()
        if sv:
            product_category_range.append({"row_id": str(cr.id), "id": str(sv.id), "value": sv.value})

    # Advertising categories
    add_cat_rows = (
        db.query(AdvertisementAddCategory)
        .filter(AdvertisementAddCategory.add_id == ad.id)
        .all()
    )
    advertising_category = []
    for acr in add_cat_rows:
        sv = db.query(SimpleValue).filter(SimpleValue.id == acr.add_category_id).first()
        if sv:
            advertising_category.append({"row_id": str(acr.id), "id": str(sv.id), "value": sv.value})

    return {
        "id": str(ad.id),
        "url": first_url or "",
        "verified": ad.verified,
        "declined": ad.declined,
        "process_id": str(ad.process_id) if ad.process_id else None,
        "first_appearance_date": str(ad.first_appearance_date) if ad.first_appearance_date else None,
        "last_appearance_date": str(ad.last_appearance_date) if ad.last_appearance_date else None,
        "brand": _sv(ad.brand_id),
        "brand_range": brand_range,
        "product_category": _sv(ad.product_category_id),
        "product_category_range": product_category_range,
        "brand_category": _sv(ad.brand_category_id),
        "advertising_category": advertising_category,
    }


# ---------------------------------------------------------------------------
# Public: get pictures for a data_prep process
# ---------------------------------------------------------------------------

def get_advertisement_pictures_for_process(db: Session, process_id: str) -> dict:
    process = get_process_instance_by_id(db, process_id)
    if not process:
        return {"unverified": [], "verified": [], "declined": [], "options": {}}

    all_ads = (
        db.query(Advertisement)
        .filter(Advertisement.process_id == process.id)
        .order_by(Advertisement.created_at)
        .all()
    )
    set_process_total_items(db, process_id, len(all_ads))

    unverified, verified, declined = [], [], []
    for ad in all_ads:
        item = _serialise_advertisement(db, ad)
        if ad.declined:
            declined.append(item)
        elif ad.verified:
            verified.append(item)
        else:
            unverified.append(item)

    return {
        "unverified": unverified,
        "verified": verified,
        "declined": declined,
        "options": _load_options(db),
    }


# ---------------------------------------------------------------------------
# Public: verify / decline
# ---------------------------------------------------------------------------

def verify_advertisement(
    db: Session,
    process_id: str,
    ad_id: str,
    brand_id: Optional[str],
    brand_range_ids: list,
    product_category_id: Optional[str],
    product_category_range_ids: list,
    brand_category_id: Optional[str],
    advertising_category_ids: list,
) -> dict:
    """
    Update FK fields on the advertisement and its related range tables,
    then mark it verified.
    """
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        return {"ok": False, "error": "Advertisement not found"}

    # Update single-FK fields
    if brand_id is not None:
        ad.brand_id = uuid.UUID(brand_id) if brand_id else None
    if product_category_id is not None:
        ad.product_category_id = uuid.UUID(product_category_id) if product_category_id else None
    if brand_category_id is not None:
        ad.brand_category_id = uuid.UUID(brand_category_id) if brand_category_id else None

    # Replace brand range
    if brand_range_ids is not None:
        db.query(AdvertisementBrand).filter(AdvertisementBrand.add_id == ad.id).delete()
        for bid in brand_range_ids:
            db.add(AdvertisementBrand(add_id=ad.id, brand_id=uuid.UUID(bid)))

    # Replace category range
    if product_category_range_ids is not None:
        db.query(AdvertisementCategory).filter(AdvertisementCategory.add_id == ad.id).delete()
        for cid in product_category_range_ids:
            db.add(AdvertisementCategory(add_id=ad.id, category_id=uuid.UUID(cid)))

    # Replace advertising categories
    if advertising_category_ids is not None:
        db.query(AdvertisementAddCategory).filter(AdvertisementAddCategory.add_id == ad.id).delete()
        for acid in advertising_category_ids:
            db.add(AdvertisementAddCategory(add_id=ad.id, add_category_id=uuid.UUID(acid)))

    ad.verified = True
    ad.declined = False
    db.commit()

    # Check how many still need review
    process = get_process_instance_by_id(db, process_id)
    if process:
        status_name = get_process_status_name(db, process)
        if status_name == "analyst_review":
            remaining = (
                db.query(Advertisement)
                .filter(
                    Advertisement.process_id == process.id,
                    Advertisement.verified == False,
                    Advertisement.declined == False,
                )
                .count()
            )
            if remaining == 0:
                update_process_status(db, process_id, "done")

    return {"ok": True}


def decline_advertisement(db: Session, process_id: str, ad_id: str) -> dict:
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        return {"ok": False, "error": "Advertisement not found"}

    ad.declined = True
    ad.verified = False
    db.commit()
    return {"ok": True}
