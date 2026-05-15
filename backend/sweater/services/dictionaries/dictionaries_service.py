
from sqlalchemy.orm import Session
from sweater.models.Dictionaries.format import Format
from sweater.models.Dictionaries.simple_value import SimpleValue
from sweater.models.Dictionaries.simple_value_type import SimpleValueType

def get_retailer_id_by_name(db: Session, retailer_name):
    if retailer_name is None:
        return None

    ref_type = db.query(SimpleValueType).filter(
        SimpleValueType.field_name == 'retailer_clean'
    ).first()
    if not ref_type:
        return None

    row = db.query(SimpleValue).filter(
        SimpleValue.value == retailer_name,
        SimpleValue.column_name_id == ref_type.id,
    ).first()
    return row.id if row else None


def get_funnel_stage_id_by_name(db: Session, funnel_stage_name: str):
    ref_type = db.query(SimpleValueType).filter(
        SimpleValueType.field_name == 'funnel_stage'
    ).first()
    if not ref_type:
        return None

    funnel_stage = db.query(SimpleValue).filter(
        SimpleValue.value.ilike(funnel_stage_name.strip().lower()),
        SimpleValue.column_name_id == ref_type.id,
    ).first()
    return funnel_stage.id if funnel_stage else None

def get_format_id(db: Session, retailer_id: str, format_name: str, cache: dict):
    if not format_name or not retailer_id:
        return None

    cache_key = f"{retailer_id}_{format_name.strip().lower()}"
    if cache_key in cache:
        return cache[cache_key]

    fmt = db.query(Format).filter(
        Format.format.ilike(format_name.strip().lower()),
        Format.retailer_id == retailer_id
    ).first()

    format_id = fmt.id if fmt else None
    cache[cache_key] = format_id
    return format_id

def get_reference_type(db: Session, reference_presetting_type: str):
    reference_type = db.query(SimpleValueType).filter(SimpleValueType.field_name.ilike(reference_presetting_type)).first()
    return reference_type