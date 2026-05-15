"""
Yandex Disk import service.

For each selected folder path:
  1. Enumerate image files inside it.
  2. Try to match folder / file name tokens against the simple_value dictionary.
  3. Insert one Advertisement row per image + one AdvertisementLink row.
  4. Mark every row with data_type='yandex_disk'.
"""

import asyncio
import re
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from sweater.models.advertisement.Advertisement_model import Advertisement
from sweater.models.advertisement.Advertisement_link_model import AdvertisementLink
from sweater.models.advertisement.Advertisement_brand_model import AdvertisementBrand
from sweater.models.advertisement.Advertisement_add_category_model import AdvertisementAddCategory
from sweater.models.Dictionaries.simple_value import SimpleValue
from sweater.models.Dictionaries.simple_value_type import SimpleValueType
from sweater.services.picture.yandex_disk_service import fetch_all_files

DATA_SOURCE_YDISK = "yandex_disk"

# ---------------------------------------------------------------------------
# Name matching helpers
# ---------------------------------------------------------------------------

def _load_all_values(db: Session) -> dict[str, list[tuple[uuid.UUID, str]]]:
    """
    Load all simple_value rows grouped by field_name.
    Returns {field_name: [(id, value), ...]}
    """
    svt_rows = db.query(SimpleValueType).all()
    result: dict[str, list[tuple[uuid.UUID, str]]] = {}
    for svt in svt_rows:
        rows = db.query(SimpleValue).filter(SimpleValue.column_name_id == svt.id).all()
        result[svt.field_name] = [(r.id, r.value) for r in rows]
    return result


def _normalise(text: str) -> str:
    """Lower-case, strip punctuation/extra spaces for comparison."""
    text = text.lower().strip()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _best_match(
    tokens: list[str],
    candidates: list[tuple[uuid.UUID, str]],
) -> Optional[uuid.UUID]:
    """
    Find the best matching candidate id for a list of text tokens.

    Strategy (ordered by confidence):
      1. Exact match on a token (case-insensitive, normalised).
      2. A candidate value that is fully contained in any token.
      3. A token that is fully contained in any candidate value.
    Returns None when nothing reasonable is found.
    """
    norm_tokens = [_normalise(t) for t in tokens]

    # Pass 1 – exact match
    for cid, cval in candidates:
        nc = _normalise(cval)
        if nc in norm_tokens:
            return cid

    # Pass 2 – candidate substring of a token
    for cid, cval in candidates:
        nc = _normalise(cval)
        for nt in norm_tokens:
            if nc and nc in nt:
                return cid

    # Pass 3 – token substring of a candidate
    for cid, cval in candidates:
        nc = _normalise(cval)
        for nt in norm_tokens:
            if nt and nt in nc:
                return cid

    return None


def _path_tokens(path: str) -> list[str]:
    """Split a disk path into its folder/file name components."""
    # path looks like:  disk:/Folder/SubFolder/file.jpg
    clean = re.sub(r"^disk:/", "", path)
    parts = [p.strip() for p in clean.replace("\\", "/").split("/") if p.strip()]
    return parts


# ---------------------------------------------------------------------------
# Main import function
# ---------------------------------------------------------------------------

async def import_selected_folders(
    db: Session,
    token: str,
    selected_paths: list[str],
    process_id: Optional[str],
) -> dict:
    """
    Import images from each of the *selected_paths* folders.
    All folder file-listings are fetched in parallel; DB writes are sequential.

    Returns {"inserted": <n>, "skipped": <n>}.
    """
    all_values = _load_all_values(db)

    # Fetch all folder file listings simultaneously
    file_results = await fetch_all_files(token, selected_paths)

    inserted = 0
    skipped = 0

    for folder_path, result in zip(selected_paths, file_results):
        if isinstance(result, Exception):
            skipped += 1
            continue
        files = result

        folder_tokens = _path_tokens(folder_path)

        # Try to resolve FK IDs from the folder path components
        retailer_id = _best_match(folder_tokens, all_values.get("retailer_clean", []))
        advertiser_id = _best_match(folder_tokens, all_values.get("advertiser", []))
        brand_id = _best_match(folder_tokens, all_values.get("brand", []))
        product_category_id = _best_match(folder_tokens, all_values.get("product_category", []))
        brand_category_id = _best_match(folder_tokens, all_values.get("brand_category", []))
        add_category_id = _best_match(folder_tokens, all_values.get("add_category", []))

        for file_info in files:
            file_tokens = folder_tokens + _path_tokens(file_info["name"])

            # Refine matches with the actual file name tokens
            eff_brand_id = _best_match(file_tokens, all_values.get("brand", [])) or brand_id
            eff_product_cat_id = (
                _best_match(file_tokens, all_values.get("product_category", []))
                or product_category_id
            )

            ad = Advertisement(
                id=uuid.uuid4(),
                process_id=uuid.UUID(process_id) if process_id else None,
                retailer_clean_id=retailer_id,
                advertiser_id=advertiser_id,
                brand_id=eff_brand_id,
                product_category_id=eff_product_cat_id,
                brand_category_id=brand_category_id,
                data_type=DATA_SOURCE_YDISK,
                verified=False,
                declined=False,
            )
            db.add(ad)
            db.flush()

            db.add(AdvertisementLink(
                add_id=ad.id,
                link=file_info["url"],
                is_incorrect=False,
            ))

            if eff_brand_id:
                db.add(AdvertisementBrand(add_id=ad.id, brand_id=eff_brand_id))

            if add_category_id:
                db.add(AdvertisementAddCategory(add_id=ad.id, add_category_id=add_category_id))

            inserted += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped}
