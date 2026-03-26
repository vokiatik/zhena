from requests import Session

from sweater.schemas.process.attribute_schema import Attribute, ProcessAttribute
from sweater.models.picture_processing.Picture_attribute_reference_crosstable_model import PictureAttributeReferenceCrosstable
from sweater.models.picture_processing.Process_attributes_crosstable_model import ProcessAttributes

def get_process_attributes_by_process_id(db: Session, process_id):
    attributes = db.query(ProcessAttributes).filter(ProcessAttributes.process_id == process_id).all()
    
    for attribute in attributes:
        reference = db.query(PictureAttributeReferenceCrosstable).filter(PictureAttributeReferenceCrosstable.process_id == process_id, PictureAttributeReferenceCrosstable.picture_attribute_id == attribute.id).first()
        if reference:
            attribute.reference_value_presetting_type = reference.reference_value_presetting_type
    return attributes

def create_process_attribute(db: Session, process_id: str, attribute: ProcessAttribute):
    new_attribute = ProcessAttributes(
        process_id=process_id,
        title=attribute.title,
        is_shown=attribute.is_shown,
        is_editable=attribute.is_editable
    )
    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)
    return new_attribute

def delete_process_attribute(db: Session, process_id, attribute_id):
    attribute = db.query(ProcessAttributes).filter(ProcessAttributes.id == attribute_id, ProcessAttributes.process_id == process_id).first()
    if not attribute:
        return None
    db.delete(attribute)
    db.commit()
    return attribute

def update_process_attribute(db: Session, process_id: str, attribute: Attribute):
    attribute_id = attribute.id
    attribute = db.query(ProcessAttributes).filter(ProcessAttributes.id == attribute_id, ProcessAttributes.process_id == process_id).first()
    if attribute:
        attribute.reference_value = attribute.reference_value
        attribute.reference_value_presetting_type_id = attribute.reference_value_presetting_type_id
        db.commit()
        db.refresh(attribute)
        return attribute
    return None

def create_process_attribute_reference_cross(db: Session, process_id: str, picture_attribute_id: str, reference_value_presetting_type_id: str):
    cross = PictureAttributeReferenceCrosstable(
        process_id=process_id,
        picture_attribute_id=picture_attribute_id,
        reference_value_presetting_type_id=reference_value_presetting_type_id
    )
    db.add(cross)
    db.commit()
    db.refresh(cross)
    return cross

def update_process_attribute_reference_cross(db: Session, process_id: str, picture_attribute_id: str, reference_value_presetting_type_id: str):
    reference = db.query(PictureAttributeReferenceCrosstable).filter(PictureAttributeReferenceCrosstable.process_id == process_id, PictureAttributeReferenceCrosstable.picture_attribute_id == picture_attribute_id).first()
    if reference:
        reference.reference_value_presetting_type_id = reference_value_presetting_type_id
        db.commit()
        db.refresh(reference)
        return reference
    return None