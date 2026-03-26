from sqlalchemy.orm import Session
from sweater.schemas.chat.Message_schema import MessageRequest
from sweater.models.chat.Message_model import Message

def create_message(db: Session, message: MessageRequest):
    db_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        content=message.content,
        timestamp=message.timestamp
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_by_chat_id(db: Session, chat_id: str):
    return db.query(Message).filter(Message.chat_id == chat_id).all()

def delete_message_by_id(db: Session, message_id: str):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        db.delete(message)
        db.commit()
        return True
    return False

