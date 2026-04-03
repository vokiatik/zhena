
from sqlalchemy.orm import Session

from sweater.models.process_settings.Picture_processing_model import ProcessSettings
from sweater.models.process_settings.Process_type_model import ProcessType
from sweater.schemas.process.process_schema import CreateProcess, UpdateProcess

def get_process_types(db: Session):
    return db.query(ProcessType).all()

def get_list_of_processes(db: Session):
    processes = db.query(ProcessSettings).all()
    return processes

def get_process_by_id(db: Session, process_id):
    process = db.query(ProcessSettings).filter(ProcessSettings.id == process_id).first()
    return process

def create_process_(db: Session, v: CreateProcess):
    new_process = ProcessSettings(
        title=v.title,
        description=v.description,
        type=v.type,
    )
    db.add(new_process)
    db.commit()
    db.refresh(new_process)
    return new_process

def update_process_(db: Session, process_id, v: UpdateProcess):
    process = db.query(ProcessSettings).filter(ProcessSettings.id == process_id).first()
    if not process:
        return None
    if v.title is not None:
        process.title = v.title
    if v.description is not None:
        process.description = v.description
    if v.type is not None:
        process.type = v.type
    db.commit()
    db.refresh(process)
    return process  

def delete_process_(db: Session, process_id):
    process = db.query(ProcessSettings).filter(ProcessSettings.id == process_id).first()
    if not process:
        return None
    db.delete(process)
    db.commit()
    return process