from sqlalchemy.orm import Session
from sweater.models.Dictionaries.simple_value import SimpleValue 
from sweater.models.Dictionaries.simple_value_type import SimpleValueType 

def get_references_by_type_(db: Session, reference_type_id: str):
    return db.query(SimpleValue).filter(
        SimpleValue.column_name_id == reference_type_id
    ).all()

def get_reference_type_name_by_id(db: Session, reference_type_id: str):
    ref_type = db.query(SimpleValueType).filter(
        SimpleValueType.id == reference_type_id
    ).first()
    return ref_type.field_name if ref_type else None
