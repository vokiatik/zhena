from requests import Session

from backend.sweater.models.Process_attributes_model import ProcessAttributes

def get_process_attributes_by_process_id(db: Session, process_id):
    attributes = db.query(ProcessAttributes).filter(ProcessAttributes.process_id == process_id).all()
    return attributes

def create_process_attribute(db: Session, process_id, title=None, is_shown=True, is_editable=True):
    new_attribute = ProcessAttributes(
        process_id=process_id,
        title=title,
        is_shown=is_shown,
        is_editable=is_editable
    )
    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)
    return new_attribute

def update_process_attribute(db: Session, attribute_id, title=None, is_shown=None, is_editable=None):
    attribute = db.query(ProcessAttributes).filter(ProcessAttributes.id == attribute_id).first()
    if not attribute:
        return None
    if title is not None:
        attribute.title = title
    if is_shown is not None:
        attribute.is_shown = is_shown
    if is_editable is not None:
        attribute.is_editable = is_editable
    db.commit()
    db.refresh(attribute)
    return attribute

def delete_process_attribute(db: Session, attribute_id):
    attribute = db.query(ProcessAttributes).filter(ProcessAttributes.id == attribute_id).first()
    if not attribute:
        return None
    db.delete(attribute)
    db.commit()
    return attribute
