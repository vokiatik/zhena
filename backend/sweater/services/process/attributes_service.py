from sqlalchemy.orm import Session

from sweater.schemas.process.attribute_schema import CreateProcessAttribute, UpdateProcessAttribute
from sweater.models.process_settings.Process_attributes_crosstable_model import ProcessAttributes
from sweater.models.advertisement.Advertisement_model import Advertisement

# Registry of available tables — add new models here as they're created
TABLE_REGISTRY = {
    "advertisement": Advertisement,
}

EXCLUDED_COLUMNS = {"id", "verified", "declined", "created_at", "user_id", "type", "process_id", "retail_processed_id"}

def get_available_tables():
    return list(TABLE_REGISTRY.keys())

def get_table_columns(table_name: str):
    model = TABLE_REGISTRY.get(table_name)
    if not model:
        return []
    return [col.key for col in model.__table__.columns if col.key not in EXCLUDED_COLUMNS]

def get_process_attributes_by_process_id(db: Session, process_id: str):
    return db.query(ProcessAttributes).filter(ProcessAttributes.process_id == process_id).all()

def create_process_attribute_(db: Session, attribute: CreateProcessAttribute):
    new_attribute = ProcessAttributes(
        process_id=attribute.process_id,
        title=attribute.title,
        is_shown=attribute.is_shown,
        is_editable=attribute.is_editable,
        is_nullable=attribute.is_nullable,
        reference_type_id=attribute.reference_type_id,
        input_type=attribute.input_type,
    )
    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)
    return new_attribute

def delete_process_attribute_(db: Session, process_id: str, attribute_id: str):
    attribute = db.query(ProcessAttributes).filter(
        ProcessAttributes.id == attribute_id,
        ProcessAttributes.process_id == process_id,
    ).first()
    if not attribute:
        return None
    db.delete(attribute)
    db.commit()
    return attribute

def update_process_attribute_(db: Session, process_id: str, attr: UpdateProcessAttribute):
    db_attr = db.query(ProcessAttributes).filter(
        ProcessAttributes.id == attr.id,
        ProcessAttributes.process_id == process_id,
    ).first()
    if not db_attr:
        return None
    if attr.is_shown is not None:
        db_attr.is_shown = attr.is_shown
    if attr.is_editable is not None:
        db_attr.is_editable = attr.is_editable
    if attr.is_nullable is not None:
        db_attr.is_nullable = attr.is_nullable
    if attr.reference_type_id is not None:
        db_attr.reference_type_id = attr.reference_type_id if attr.reference_type_id != "" else None
    if attr.input_type is not None:
        db_attr.input_type = attr.input_type
    db.commit()
    db.refresh(db_attr)
    return db_attr