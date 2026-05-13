"""
Parses an uploaded file into the new advertisement-centric table structure.

Expected columns (after normalisation):
    retailer_clean, advertiser, brand, product_category, brand_category,
    first_appearance_date, last_appearance_date,
    format,
    link, appearance_period,
    group_id   (used to group multi-row entries sharing one advertisement)

For each unique group_id (or single row when no group_id):
  1. Insert one row into advertisement (using the first row of the group for FKs).
  2. Insert rows into advertisement_link.
  3. Insert rows into advertisement_brand   (one per brand value).
  4. Insert rows into advertisement_category (one per product_category value).
  5. Insert rows into advertisement_format.
  6. Insert rows into advertisement_add_category (from advertising_category column).
"""

import uuid
from io import BytesIO
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from sweater.routes.upload.read_csv_with_fallbacks import read_csv_with_fallbacks
from sweater.models.advertisement.Advertisement_model import Advertisement
from sweater.models.advertisement.Advertisement_link_model import AdvertisementLink
from sweater.models.advertisement.Advertisement_brand_model import AdvertisementBrand
from sweater.models.advertisement.Advertisement_category_model import AdvertisementCategory
from sweater.models.advertisement.Advertisement_format_model import AdvertisementFormat
from sweater.models.advertisement.Advertisement_add_category_model import AdvertisementAddCategory
from sweater.models.Dictionaries.simple_value import SimpleValue
from sweater.models.Dictionaries.simple_value_type import SimpleValueType
from sweater.models.Dictionaries.format import Format
from sweater.models.Dictionaries.detector_format_comparison import DetectorFormatComparison
from sweater.services.upload.advertisement_validation_service import (
    SIMPLE_VALUE_COLUMN_MAP,
    split_multi_value,
)


# ---------------------------------------------------------------------------
# Expected file columns → normalised DB column names
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "retailer_clean",
    "advertiser",
    "brand",
    "product_category",
    "brand_category",
    "first_appearance_date",
    "last_appearance_date",
    "format",
    "link",
    "appearance_period",
    "group_id",
]

# Display-friendly aliases accepted in uploaded files
FILE_COLUMN_ALIASES = {
    "Ретейлер clean": "retailer_clean",
    "Advertiser (producer)": "advertiser",
    "Brands list clean": "brand",
    "!Категория Ферреро": "product_category",
    "Product category": "!Категория Ферреро  (Range категорий)",
    "Brand category": "!Категория Ферреро (Мультибренд категорий)",
    "Дата первого скрина": "first_appearance_date",
    "Дата последнего скрина": "last_appearance_date",
    "!Формат": "format",
    "Advertisement ID": "link",
    "Количество дней размещения est.": "appearance_period",
    "group_id": "group_id",
}


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------

def parse_advertisement_file(filename: str, content: bytes) -> pd.DataFrame:
    lower = filename.lower()
    if lower.endswith(".csv"):
        df = read_csv_with_fallbacks(content)
    elif lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type. Only CSV, XLSX and XLS are allowed.")

    df.columns = [str(c).strip() for c in df.columns]

    # Normalise column names via aliases
    df.rename(columns=FILE_COLUMN_ALIASES, inplace=True)

    # Check for at least the mandatory columns
    mandatory = {"retailer_clean", "advertiser", "brand", "first_appearance_date", "last_appearance_date", "format"}
    missing_cols = mandatory - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_cols))}")

    # Add optional columns with empty defaults
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[EXPECTED_COLUMNS].copy()

    for date_col in ("first_appearance_date", "last_appearance_date"):
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.date

    df = df.where(pd.notnull(df), None)
    return df


# ---------------------------------------------------------------------------
# DB lookup helpers
# ---------------------------------------------------------------------------

def _get_simple_value_id(
    db: Session,
    field_name: str,
    raw_value: Optional[str],
    cache: dict,
) -> Optional[uuid.UUID]:
    """Look up (or cache) simple_value.id for a given field_name + raw value."""
    if raw_value is None:
        return None
    key = (field_name, raw_value.strip().upper())
    if key in cache:
        return cache[key]

    svt = db.query(SimpleValueType).filter(SimpleValueType.field_name == field_name).first()
    if not svt:
        return None

    sv = db.query(SimpleValue).filter(
        SimpleValue.column_name_id == svt.id,
        SimpleValue.value == raw_value.strip(),
    ).first()
    result = sv.id if sv else None
    cache[key] = result
    return result


def _get_format_id(
    db: Session,
    retailer_clean_id: Optional[uuid.UUID],
    raw_value: Optional[str],
    cache: dict,
) -> Optional[uuid.UUID]:
    """Look up format.id; falls back to detector_format_comparison."""
    if raw_value is None:
        return None
    key = raw_value.strip().upper()
    if key in cache:
        return cache[key]

    fmt = db.query(Format).filter(Format.format.ilike(raw_value.strip())).first()
    if fmt:
        cache[key] = fmt.id
        return fmt.id

    det = db.query(DetectorFormatComparison).filter(
        DetectorFormatComparison.retailer_id == retailer_clean_id,
        DetectorFormatComparison.detector_format.ilike(raw_value.strip())
    ).first()
    result = det.format_id if det else None
    cache[key] = result
    return result


# ---------------------------------------------------------------------------
# Main save function
# ---------------------------------------------------------------------------

def save_advertisement_dataframe_to_db(
    db: Session,
    df: pd.DataFrame,
    process_id: Optional[str] = None,
) -> int:
    """
    Insert all rows from *df* into the advertisement table family.
    Returns the number of advertisement rows inserted.
    """
    sv_cache: dict = {}     # (field_name, value_upper) → UUID
    fmt_cache: dict = {}    # format_upper → UUID

    inserted = 0

    # Group by group_id; rows without a group_id each form their own group
    df = df.copy()
    df["_group"] = df["group_id"].apply(lambda v: str(v) if pd.notnull(v) and str(v).strip() else None)
    df["_auto_group"] = df.apply(
        lambda r: r["_group"] if r["_group"] else f"__auto_{r.name}", axis=1
    )

    for group_key, group_df in df.groupby("_auto_group", sort=False):
        first = group_df.iloc[0]

        # ── 1. Resolve FK IDs from first row ────────────────────────────
        retailer_clean_id = _get_simple_value_id(
            db, "retailer_clean", first.get("retailer_clean"), sv_cache
        )
        advertiser_id = _get_simple_value_id(
            db, "advertiser", first.get("advertiser"), sv_cache
        )
        # Primary brand FK – first brand from the first row
        raw_brand = first.get("brand")
        first_brand = split_multi_value(str(raw_brand))[0] if raw_brand else None
        brand_id = _get_simple_value_id(db, "brand", first_brand, sv_cache)

        # Primary product_category FK – first value from first row
        raw_cat = first.get("product_category")
        first_cat = split_multi_value(str(raw_cat))[0] if raw_cat else None
        product_category_id = _get_simple_value_id(db, "product_category", first_cat, sv_cache)

        brand_category_id = _get_simple_value_id(
            db, "brand_category", first.get("brand_category"), sv_cache
        )

        # ── 2. Insert advertisement row ──────────────────────────────────
        ad = Advertisement(
            id=uuid.uuid4(),
            process_id=process_id,
            retailer_clean_id=retailer_clean_id,
            advertiser_id=advertiser_id,
            brand_id=brand_id,
            product_category_id=product_category_id,
            brand_category_id=brand_category_id,
            first_appearance_date=first.get("first_appearance_date"),
            last_appearance_date=first.get("last_appearance_date"),
            data_type="file",
            verified=False,
            declined=False,
        )
        db.add(ad)
        db.flush()  # get ad.id before inserting child rows

        # ── 3. Links (one per row in the group) ─────────────────────────
        for _, row in group_df.iterrows():
            link_val = row.get("link")
            period_val = row.get("appearance_period")
            if link_val or period_val:
                db.add(AdvertisementLink(
                    add_id=ad.id,
                    link=str(link_val) if link_val else None,
                    appearance_period=str(period_val) if period_val else None,
                ))

        # ── 4. Brand range (all brand values across whole group) ─────────
        seen_brands: set = set()
        for _, row in group_df.iterrows():
            raw = row.get("brand")
            if not raw:
                continue
            for part in split_multi_value(str(raw)):
                if part.upper() in seen_brands:
                    continue
                seen_brands.add(part.upper())
                bid = _get_simple_value_id(db, "brand", part, sv_cache)
                if bid:
                    db.add(AdvertisementBrand(add_id=ad.id, brand_id=bid))

        # ── 5. Category range ────────────────────────────────────────────
        seen_cats: set = set()
        for _, row in group_df.iterrows():
            raw = row.get("product_category")
            if not raw:
                continue
            for part in split_multi_value(str(raw)):
                if part.upper() in seen_cats:
                    continue
                seen_cats.add(part.upper())
                cid = _get_simple_value_id(db, "product_category", part, sv_cache)
                if cid:
                    db.add(AdvertisementCategory(add_id=ad.id, category_id=cid))

        # ── 6. Format (from first row) ───────────────────────────────────
        fmt_id = _get_format_id(db, retailer_clean_id, first.get("format"), fmt_cache)
        if fmt_id:
            db.add(AdvertisementFormat(add_id=ad.id, format_id=fmt_id))

        inserted += 1

    db.commit()
    return inserted


# ---------------------------------------------------------------------------
# Link parsing stage (placeholder)
# ---------------------------------------------------------------------------

def parse_links_placeholder(process_id: str) -> None:
    """Placeholder: download pictures from collected links. To be implemented."""
    pass
