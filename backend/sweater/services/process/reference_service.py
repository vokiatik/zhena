from sqlalchemy.orm import Session

from sweater.models.picture_processing.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.picture_processing.Picture_attribute_reference_type_model import PictureAttributeReferenceType

def list_reference_types_(db: Session):
    return db.query(PictureAttributeReferenceType).where(PictureAttributeReferenceType.deleted == False).all()

def get_references_by_type_(db: Session, reference_type_id: str):
    return db.query(PictureAttributeReference).filter(
        PictureAttributeReference.reference_value_presetting_type_id == reference_type_id
    ).all()

def create_reference_type_(db: Session, reference_type: str):
    new_reference_type = PictureAttributeReferenceType(reference_value=reference_type)
    db.add(new_reference_type)
    db.commit()
    db.refresh(new_reference_type)
    return new_reference_type

def delete_reference_type_(db: Session, reference_type_id: str):
    reference_type = db.query(PictureAttributeReferenceType).filter(
        PictureAttributeReferenceType.id == reference_type_id
    ).first()
    if not reference_type:
        return {"success": False, "error": "Reference type not found"}
    reference_type.deleted = True
    db.commit()
    return {"success": True, "message": "Reference type deleted"}

def add_value_to_reference_(db: Session, reference_type_id: str, value: str):
    new_ref = PictureAttributeReference(
        reference_value=value,
        reference_value_presetting_type_id=reference_type_id,
    )
    db.add(new_ref)
    db.commit()
    db.refresh(new_ref)
    return new_ref

def delete_value_from_reference_(db: Session, reference_id: str):
    reference = db.query(PictureAttributeReference).filter(
        PictureAttributeReference.id == reference_id
    ).first()
    if not reference:
        return {"success": False, "error": "Reference value not found"}
    db.delete(reference)
    db.commit()
    return {"success": True, "message": "Value deleted"}

def update_value_of_reference_(db: Session, reference_id: str, new_value: str):
    reference = db.query(PictureAttributeReference).filter(
        PictureAttributeReference.id == reference_id
    ).first()
    if not reference:
        return {"success": False, "error": "Reference value not found"}
    reference.reference_value = new_value
    db.commit()
    db.refresh(reference)
    return reference