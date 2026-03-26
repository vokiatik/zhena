from requests import Session

from sweater.models.picture_processing.Picture_attribute_reference_model import PictureAttributeReference
from sweater.models.picture_processing.Picture_attribute_reference_type_model import PictureAttributeReferenceType

def list_reference_types_(db: Session):
    ref_type = db.query(PictureAttributeReferenceType).where(PictureAttributeReferenceType.deleted == False).all()
    return ref_type

def get_references_by_type_(db: Session, reference_type_id: str):
    references = db.query(PictureAttributeReference).filter(PictureAttributeReference.reference_value_presetting_type_id == reference_type_id).all()
    return references

def create_reference_type_(db: Session, reference_type: str):
    new_reference_type = PictureAttributeReferenceType(reference_value=reference_type)
    db.add(new_reference_type)
    db.commit()
    db.refresh(new_reference_type)
    return new_reference_type

def delete_reference_type_(db: Session, reference_type_id: str):
    reference_type = db.query(PictureAttributeReferenceType).filter(PictureAttributeReferenceType.id == reference_type_id).first()
    if reference_type:
        reference_type.deleted = True
        db.commit()
        return {"message": "Reference deleted successfully"}
    else:
        return {"message": "Reference not found"}
    
def add_value_to_reference_(db: Session, reference_id: str, value: str):
    reference = db.query(PictureAttributeReference).filter(PictureAttributeReference.id == reference_id).first()
    if reference:
        reference.reference_value = value
        db.commit()
        db.refresh(reference)
        return reference
    else:
        return {"message": "Reference not found"}
    
def delete_value_from_reference_(db: Session, reference_id: str):
    reference = db.query(PictureAttributeReference).filter(PictureAttributeReference.id == reference_id).first()
    if reference:
        reference.reference_value = None
        db.commit()
        db.refresh(reference)
        return {"message": "Value deleted successfully"}
    else:
        return {"message": "Reference not found"}
    
def update_value_of_reference_(db: Session, reference_id: str, new_value: str):
    reference = db.query(PictureAttributeReference).filter(PictureAttributeReference.id == reference_id).first()
    if reference:
        reference.reference_value = new_value
        db.commit()
        db.refresh(reference)
        return reference
    else:
        return {"message": "Reference not found"}