"""
Service that checks whether all values in attribute-mapped columns of an uploaded
DataFrame already exist in the reference table.  If any are missing it returns
them grouped by reference type so the caller can ask the user what to do.
"""

from typing import Dict, List, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from sweater.models.process_settings.Picture_attribute_reference_model import (
    PictureAttributeReference,
)
from sweater.models.process_settings.Picture_attribute_reference_type_model import (
    PictureAttributeReferenceType,
)
from sweater.models.process_settings.Picture_processing_model import ProcessSettings
from sweater.models.process_settings.Process_attributes_crosstable_model import (
    ProcessAttributes,
)
from sweater.models.process_settings.Process_type_model import ProcessType
from sweater.schemas.fileUpload.file_upload_shcema import (
    ConfirmDecision,
    MissingReferenceValue,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_file_process_settings(db: Session) -> List[ProcessSettings]:
    """Return all ProcessSettings whose type maps to a ProcessType with
    process_type_name == 'file'."""
    file_types = (
        db.query(ProcessType)
        .filter(ProcessType.process_type_name == "file")
        .all()
    )
    print(f"[VALIDATION DEBUG] ProcessTypes with name='file': {[(str(pt.id), pt.process_type_name) for pt in file_types]}")
    if not file_types:
        print("[VALIDATION DEBUG] No ProcessType named 'file' found — check db_seed was run")
        return []

    type_ids = [pt.id for pt in file_types]
    result = (
        db.query(ProcessSettings)
        .filter(ProcessSettings.type.in_(type_ids))
        .all()
    )
    print(f"[VALIDATION DEBUG] ProcessSettings with file type: {[(str(ps.id), ps.title) for ps in result]}")
    return result


def _get_attributes_with_reference(
    db: Session, process_settings_list: List[ProcessSettings]
) -> List[ProcessAttributes]:
    """Return all ProcessAttributes (with a reference_type_id set) for the
    given list of ProcessSettings."""
    if not process_settings_list:
        return []

    process_ids = [ps.id for ps in process_settings_list]
    result = (
        db.query(ProcessAttributes)
        .filter(
            ProcessAttributes.process_id.in_(process_ids),
            ProcessAttributes.reference_type_id.isnot(None),
        )
        .all()
    )
    print(f"[VALIDATION DEBUG] ProcessAttributes with reference_type_id: {[(str(a.id), a.title, str(a.reference_type_id)) for a in result]}")
    return result


def _existing_values_for_type(db: Session, reference_type_id) -> List[str]:
    rows = (
        db.query(PictureAttributeReference)
        .filter(PictureAttributeReference.reference_type_id == reference_type_id)
        .all()
    )
    return [r.reference_value for r in rows]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_missing_reference_values(
    db: Session, df: pd.DataFrame
) -> Tuple[List[MissingReferenceValue], Dict[str, List[str]]]:
    """
    Scan *df* for columns that are mapped to a reference type via ProcessAttributes.
    Return:
      - list of MissingReferenceValue (one entry per distinct missing value per column)
      - dict { type_id -> [existing values] } for types that have at least one missing value
        (so the frontend can populate the "replace with" dropdown)
    """
    process_settings_list = _get_file_process_settings(db)
    if not process_settings_list:
        return [], {}

    attributes = _get_attributes_with_reference(db, process_settings_list)
    if not attributes:
        return [], {}

    print(f"[VALIDATION DEBUG] DataFrame columns: {list(df.columns)}")

    missing: List[MissingReferenceValue] = []
    types_with_missing: set = set()

    for attr in attributes:
        column_name = attr.title
        if column_name not in df.columns:
            print(f"[VALIDATION DEBUG] Attribute title '{column_name}' NOT in DataFrame columns — skipping")
            continue

        ref_type_id = str(attr.reference_type_id)

        # Unique non-null values from the file column
        file_values = {
            str(v).strip()
            for v in df[column_name].dropna().unique()
            if str(v).strip()
        }
        if not file_values:
            continue

        # Values already in reference table for this type
        existing = set(_existing_values_for_type(db, attr.reference_type_id))
        print(f"[VALIDATION DEBUG] Column '{column_name}': {len(file_values)} unique file values, {len(existing)} existing in DB, {len(file_values - existing)} missing")

        # Resolve type name
        ref_type_obj = db.query(PictureAttributeReferenceType).filter(
            PictureAttributeReferenceType.id == attr.reference_type_id
        ).first()
        type_name = ref_type_obj.reference_type_name if ref_type_obj else ref_type_id

        for val in sorted(file_values - existing):
            missing.append(
                MissingReferenceValue(
                    type_id=ref_type_id,
                    type_name=type_name,
                    column=column_name,
                    value=val,
                )
            )
            types_with_missing.add(ref_type_id)

    # Build existing-values map only for types that have missing values
    existing_values_by_type: Dict[str, List[str]] = {}
    for type_id in types_with_missing:
        from uuid import UUID
        try:
            tid_uuid = UUID(type_id)
        except ValueError:
            continue
        existing_values_by_type[type_id] = sorted(
            _existing_values_for_type(db, tid_uuid)
        )

    return missing, existing_values_by_type


def apply_decisions_to_df(df: pd.DataFrame, decisions: List[ConfirmDecision]) -> pd.DataFrame:
    """
    Apply user decisions to the DataFrame **before** it is saved to the DB:
      - If replace_with is set → replace that value in the column.
      - Otherwise the original value stays (it will be saved as a new reference entry).
    Returns a copy of the DataFrame.
    """
    df = df.copy()
    for decision in decisions:
        if not decision.save and decision.replace_with:
            col = decision.column
            if col in df.columns:
                df[col] = df[col].replace(decision.original_value, decision.replace_with)
    return df


def save_new_reference_values(db: Session, decisions: List[ConfirmDecision]) -> None:
    """Persist all decisions where save=True as new PictureAttributeReference rows."""
    from uuid import UUID

    for decision in decisions:
        if not decision.save:
            continue
        try:
            type_uuid = UUID(decision.type_id)
        except ValueError:
            continue

        # Avoid duplicates
        exists = (
            db.query(PictureAttributeReference)
            .filter(
                PictureAttributeReference.reference_type_id == type_uuid,
                PictureAttributeReference.reference_value == decision.original_value,
            )
            .first()
        )
        if not exists:
            new_ref = PictureAttributeReference(
                reference_value=decision.original_value,
                reference_type_id=type_uuid,
            )
            db.add(new_ref)

    db.commit()
