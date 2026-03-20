from sqlalchemy.orm import Session
from sweater.schemas.chat.Chat_schema import ChatRequest
from sweater.models.Chat_model import Chat

def create_chat(db: Session, chat: ChatRequest):
    db_chat = Chat(
        user_id=chat.user_id,
        message=chat.message,
        timestamp=chat.timestamp
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chats_by_user_id(db: Session, user_id: str):
    return db.query(Chat).filter(Chat.user_id == user_id).all()

def delete_chat_by_id(db: Session, chat_id: str):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat:
        db.delete(chat)
        db.commit()
        return True
    return False

def get_user_id_by_chat_id(db: Session, chat_id: str):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    return chat.user_id if chat else None

# def update_chat_message(db: Session, chat_id: str, new_message: str):
#     chat = db.query(Chat).filter(Chat.id == chat_id).first()
#     if chat:
#         chat.message = new_message
#         db.commit()
#         db.refresh(chat)
#         return chat
#     return None
