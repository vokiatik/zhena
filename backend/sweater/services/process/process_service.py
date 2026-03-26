
from requests import Session

from sweater.models.picture_processing.Picture_processing_model import PictureProcessing
from sweater.schemas.process.process_schema import UpdateProcess

def get_list_of_processes(db: Session,):
    processes = db.query(PictureProcessing).all()
    return processes

def get_process_by_id(db: Session, process_id):
    process = db.query(PictureProcessing).filter(PictureProcessing.id == process_id).first()
    return process

def create_process_(db: Session, v: UpdateProcess, responsible_user_id=None):
    new_process = PictureProcessing(
        title=v.title,
        description=v.description,
        responsible_user_id=responsible_user_id
    )
    db.add(new_process)
    db.commit()
    db.refresh(new_process)
    return new_process

def update_process_(db: Session, process_id, v: UpdateProcess, responsible_user_id=None):
    process = db.query(PictureProcessing).filter(PictureProcessing.id == process_id).first()
    if not process:
        return None
    if v.title is not None:
        process.title = v.title
    if v.description is not None:
        process.description = v.description
    if responsible_user_id is not None:
        process.responsible_user_id = responsible_user_id
    db.commit()
    db.refresh(process)
    return process  

def delete_process_(db: Session, process_id):
    process = db.query(PictureProcessing).filter(PictureProcessing.id == process_id).first()
    if not process:
        return None
    db.delete(process)
    db.commit()
    return process