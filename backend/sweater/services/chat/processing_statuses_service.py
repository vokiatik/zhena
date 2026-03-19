from sqlalchemy.orm import Session
from backend.sweater.schemas.chat.Processing_status_schema import ProcessingStatus
from backend.sweater.models.Processing_statuses_model import ProcessingStatus

def create_processing_status(db: Session, processing_status: ProcessingStatus):
    db_processing_status = ProcessingStatus(
        message_id=processing_status.message_id,
        status=processing_status.status,
        label=processing_status.label,
        created_at=processing_status.created_at
    )
    db.add(db_processing_status)
    db.commit()
    db.refresh(db_processing_status)
    return db_processing_status

