
from requests import Session

from backend.sweater.models.File_processing_model import FileProcessing


def get_list_of_processes(db: Session,):
    processes = db.query(FileProcessing).all()
    return processes

def get_process_by_id(db: Session, process_id):
    process = db.query(FileProcessing).filter(FileProcessing.id == process_id).first()
    return process

def create_process(db: Session, title, description, responsible_user_id):
    new_process = FileProcessing(
        title=title,
        description=description,
        responsible_user_id=responsible_user_id
    )
    db.add(new_process)
    db.commit()
    db.refresh(new_process)
    return new_process

def update_process(db: Session, process_id, title=None, description=None, responsible_user_id=None):
    process = db.query(FileProcessing).filter(FileProcessing.id == process_id).first()
    if not process:
        return None
    if title is not None:
        process.title = title
    if description is not None:
        process.description = description
    if responsible_user_id is not None:
        process.responsible_user_id = responsible_user_id
    db.commit()
    db.refresh(process)
    return process  

def delete_process(db: Session, process_id):
    process = db.query(FileProcessing).filter(FileProcessing.id == process_id).first()
    if not process:
        return None
    db.delete(process)
    db.commit()
    return process