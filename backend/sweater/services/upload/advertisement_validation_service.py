"""
Validates an uploaded DataFrame against the new simple_value / format dictionaries.

Steps:
  1. Check simple-value columns (retailer_clean, advertiser, brand_clean,
     product_category, brand_category) against simple_value table.
  2. Check the format column against the format table; fall back to
     detector_format_comparison for unrecognised values.
  3. Split multi-value brand/category cells (/, \\, ;, comma, parentheses).

Returns missing values grouped by field_name so the caller can ask the
user to either map them to an existing entry or add them to the dictionary.
"""

import re
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import pandas as pd
from sqlalchemy.orm import Session

from sweater.models.Dictionaries.simple_value import SimpleValue
from sweater.models.Dictionaries.simple_value_type import SimpleValueType
from sweater.models.Dictionaries.format import Format
from sweater.models.Dictionaries.detector_format_comparison import DetectorFormatComparison


# ---------------------------------------------------------------------------
# Column → simple_value field_name mapping
# ---------------------------------------------------------------------------

# Maps DataFrame column names (as they appear after parsing) to the
# field_name stored in simple_value_type.
SIMPLE_VALUE_COLUMN_MAP: Dict[str, str] = {
    "retailer_clean": "retailer_clean",
    "advertiser": "advertiser",
    "brand": "brand",
    "product_category": "product_category",
    "brand_category": "brand_category",
}

# Columns whose values may contain multiple entries separated by various chars
MULTI_VALUE_COLUMNS = {"brand", "product_category"}

MULTI_VALUE_SEPARATORS = re.compile(r"[/\\;,()]+")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_type_id(db: Session, field_name: str) -> Optional[UUID]:
    svt = db.query(SimpleValueType).filter(SimpleValueType.field_name == field_name).first()
    return svt.id if svt else None


def _get_existing_values(db: Session, type_id: UUID) -> Dict[str, UUID]:
    """Return {normalised_value: id} for all simple_value rows of given type."""
    rows = db.query(SimpleValue).filter(SimpleValue.column_name_id == type_id).all()
    return {r.value.strip().upper(): r.id for r in rows}


def split_multi_value(raw: str) -> List[str]:
    """Split a cell that may hold multiple values separated by /, \\, ;, , or ()."""
    parts = MULTI_VALUE_SEPARATORS.split(raw)
    return [p.strip() for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MissingValue:
    def __init__(self, field: str, value: str):
        self.field = field   # field_name (e.g. 'brand')
        self.value = value   # original raw value


def validate_simple_values(
    db: Session, df: pd.DataFrame
) -> Tuple[List[MissingValue], Dict[str, List[str]]]:
    """
    Validate all simple-value columns in *df*.

    Returns:
        missing   – list of MissingValue objects
        existing  – {field_name: [value, ...]} for each validated column
    """
    missing: List[MissingValue] = []
    existing_by_field: Dict[str, List[str]] = {}

    for col, field_name in SIMPLE_VALUE_COLUMN_MAP.items():
        if col not in df.columns:
            continue

        type_id = _get_type_id(db, field_name)
        if type_id is None:
            continue  # type not seeded yet – skip silently

        existing = _get_existing_values(db, type_id)
        existing_by_field[field_name] = list(existing.keys())

        for raw in df[col].dropna().unique():
            if not raw:
                continue

            if col in MULTI_VALUE_COLUMNS:
                parts = split_multi_value(raw)
            else:
                parts = [raw]

            for part in parts:
                if part.upper() not in existing:
                    missing.append(MissingValue(field=field_name, value=part))

    missing = list({(m.field, m.value): m for m in missing}.values())  # deduplicate
    missing.sort(key=lambda m: (m.field, m.value))
    return missing, existing_by_field


def validate_formats(
    db: Session, df: pd.DataFrame
) -> Tuple[List[MissingValue], Dict[str, UUID]]:
    """
    Validate the 'format' column in *df*.

    First checks format.format for an exact match (case-insensitive).
    Falls back to detector_format_comparison.detector_format.

    Returns:
        missing        – MissingValue list for values not found anywhere
        format_id_map  – {raw_value_upper: format_id} for resolved values
    """
    missing: List[MissingValue] = []
    format_id_map: Dict[str, UUID] = {}

    if "format" not in df.columns:
        return missing, format_id_map

    # Build lookup caches
    formats = db.query(Format).all()
    format_by_name: Dict[str, UUID] = {
        f.format.strip().upper(): f.id for f in formats if f.format
    }

    detector_rows = db.query(DetectorFormatComparison).all()
    detector_map: Dict[str, UUID] = {
        d.detector_format.strip().upper(): d.format_id
        for d in detector_rows
        if d.detector_format and d.format_id
    }

    for raw in df["format"].dropna().unique():
        raw_str = str(raw).strip()
        if not raw_str:
            continue
        key = raw_str.upper()

        if key in format_by_name:
            format_id_map[key] = format_by_name[key]
        elif key in detector_map:
            format_id_map[key] = detector_map[key]
        else:
            missing.append(MissingValue(field="format", value=raw_str))

    return missing, format_id_map


FORMAT_TYPE_ID = "format"


def check_all_missing(
    db: Session, df: pd.DataFrame
) -> Tuple[List[dict], Dict[str, List[str]]]:
    """
    Convenience wrapper that runs both simple-value and format validation.

    Returns:
        missing_list  – list of {type_id, type_name, column, value} dicts
        existing_map  – {type_id: [existing_value, ...]}
    """
    # Build type_id lookup from SimpleValueType
    svt_rows = db.query(SimpleValueType).all()
    type_id_by_field: Dict[str, str] = {svt.field_name: str(svt.id) for svt in svt_rows}

    sv_missing, existing_by_field = validate_simple_values(db, df)
    fmt_missing, _ = validate_formats(db, df)

    # Build existing_by_type keyed by type_id string
    existing_by_type: Dict[str, List[str]] = {}
    for field_name, values in existing_by_field.items():
        tid = type_id_by_field.get(field_name, field_name)
        existing_by_type[tid] = values
    existing_by_type[FORMAT_TYPE_ID] = [
        f.format for f in db.query(Format).all() if f.format
    ]

    # Build missing list with type info
    missing_list: List[dict] = []
    for m in sv_missing:
        tid = type_id_by_field.get(m.field, m.field)
        missing_list.append({
            "type_id": tid,
            "type_name": m.field,
            "column": m.field,
            "value": m.value,
        })
    for m in fmt_missing:
        missing_list.append({
            "type_id": FORMAT_TYPE_ID,
            "type_name": "format",
            "column": "format",
            "value": m.value,
        })

    return missing_list, existing_by_type


def apply_simple_value_decisions(
    df: pd.DataFrame,
    decisions: List[dict],
) -> pd.DataFrame:
    """
    Apply user decisions (replace_with / save) to the DataFrame in-place.
    Each decision: {field, original_value, replace_with, save}
    """
    replace_map: Dict[Tuple[str, str], str] = {}
    for d in decisions:
        if not d.get("save") and d.get("replace_with"):
            col = _field_to_col(d.get("column") or d.get("field", ""))
            if col:
                replace_map[(col, d["original_value"].strip().upper())] = d["replace_with"]

    for col, field_name in SIMPLE_VALUE_COLUMN_MAP.items():
        if col not in df.columns:
            continue
        for (target_col, orig_upper), replacement in replace_map.items():
            if target_col != col:
                continue
            df[col] = df[col].apply(
                lambda v, o=orig_upper, r=replacement: r if str(v).strip().upper() == o else v
            )
    return df


def save_new_simple_values(db: Session, decisions: List[dict]) -> None:
    """Persist new simple_value rows for decisions where save=True."""
    for d in decisions:
        if not d.get("save"):
            continue
        field_name = d.get("column") or d.get("field")
        if not field_name:
            continue
        value = d["original_value"].strip()

        type_id = _get_type_id(db, field_name)
        if not type_id:
            continue

        existing = _get_existing_values(db, type_id)
        if value.upper() in existing:
            continue

        db.add(SimpleValue(column_name_id=type_id, value=value))

    db.commit()


def save_new_format(db: Session, format_value: str, detector_value: Optional[str] = None) -> UUID:
    """Create a new Format row and optionally link a detector_format entry."""
    new_fmt = Format(format=format_value)
    db.add(new_fmt)
    db.flush()  # get the id

    if detector_value:
        db.add(DetectorFormatComparison(
            detector_format=detector_value,
            format_id=new_fmt.id,
        ))

    db.commit()
    db.refresh(new_fmt)
    return new_fmt.id


def save_new_detector_mapping(db: Session, detector_value: str, format_id: UUID) -> None:
    """Add a detector_format_comparison row mapping detector_value → format_id."""
    db.add(DetectorFormatComparison(detector_format=detector_value, format_id=format_id))
    db.commit()


# ---------------------------------------------------------------------------
# Internal util
# ---------------------------------------------------------------------------

def _field_to_col(field_name: str) -> Optional[str]:
    """Reverse-lookup: field_name → DataFrame column name."""
    for col, fn in SIMPLE_VALUE_COLUMN_MAP.items():
        if fn == field_name:
            return col
    return None
