import uuid
from sqlalchemy.orm import Session

from sweater.models.process_settings.Process_model import Process
from sweater.models.process_settings.Process_type_model import ProcessType
from sweater.models.process_settings.Process_status_model import ProcessStatus


def get_process_type_by_name(db: Session, name: str) -> ProcessType | None:
    return db.query(ProcessType).filter(ProcessType.process_type_name == name).first()


def get_process_status_by_name(db: Session, name: str) -> ProcessStatus | None:
    return db.query(ProcessStatus).filter(ProcessStatus.process_status_name == name).first()


def get_process_instance_by_id(db: Session, process_id: str) -> Process | None:
    return db.query(Process).filter(Process.id == process_id).first()


def list_process_instances(db: Session):
    processes = db.query(Process).order_by(Process.created_at.desc()).all()
    result = []
    for p in processes:
        ptype = db.query(ProcessType).filter(ProcessType.id == p.type_id).first()
        pstatus = db.query(ProcessStatus).filter(ProcessStatus.id == p.status_id).first()
        result.append({
            "id": str(p.id),
            "type_name": ptype.process_type_name if ptype else "unknown",
            "type_id": str(p.type_id),
            "status_name": pstatus.process_status_name if pstatus else "unknown",
            "status_id": str(p.status_id) if p.status_id else None,
            "comment": p.comment,
            "initiator_id": str(p.initiator_id) if p.initiator_id else None,
            "total_items": p.total_items,
            "parent_process_id": str(p.parent_process_id) if p.parent_process_id else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    return result


def create_process_instance(
    db: Session,
    type_name: str,
    comment: str | None,
    initiator_id: str | None,
    parent_process_id: str | None = None,
) -> Process:
    ptype = get_process_type_by_name(db, type_name)
    if not ptype:
        raise ValueError(f"Process type '{type_name}' not found")

    pstatus = get_process_status_by_name(db, "initiated")
    if not pstatus:
        raise ValueError("Process status 'initiated' not found")

    process = Process(
        id=uuid.uuid4(),
        type_id=ptype.id,
        status_id=pstatus.id,
        comment=comment,
        initiator_id=initiator_id,
        parent_process_id=parent_process_id,
    )
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


def update_process_status(db: Session, process_id: str, status_name: str):
    process = get_process_instance_by_id(db, process_id)
    if not process:
        return None

    pstatus = get_process_status_by_name(db, status_name)
    if not pstatus:
        return None

    process.status_id = pstatus.id
    db.commit()
    db.refresh(process)
    return process


def set_process_total_items(db: Session, process_id: str, total: int):
    process = get_process_instance_by_id(db, process_id)
    if process and process.total_items is None:
        process.total_items = total
        db.commit()


def get_process_type_name(db: Session, process: Process) -> str:
    ptype = db.query(ProcessType).filter(ProcessType.id == process.type_id).first()
    return ptype.process_type_name if ptype else "unknown"


def get_process_status_name(db: Session, process: Process) -> str:
    pstatus = db.query(ProcessStatus).filter(ProcessStatus.id == process.status_id).first()
    return pstatus.process_status_name if pstatus else "unknown"
