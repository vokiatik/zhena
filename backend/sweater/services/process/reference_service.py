from sqlalchemy.orm import Session

from sweater.models.process_settings.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.process_settings.Picture_attribute_reference_type_model import PictureAttributeReferenceType

def get_references_by_type_(db: Session, reference_type_id: str):
    return db.query(PictureAttributeReference).filter(
        PictureAttributeReference.reference_type_id == reference_type_id
    ).all()

def get_reference_type_name_by_id(db: Session, reference_type_id: str):
    ref_type = db.query(PictureAttributeReferenceType).filter(
        PictureAttributeReferenceType.id == reference_type_id
    ).first()
    return ref_type.reference_type_name if ref_type else None
