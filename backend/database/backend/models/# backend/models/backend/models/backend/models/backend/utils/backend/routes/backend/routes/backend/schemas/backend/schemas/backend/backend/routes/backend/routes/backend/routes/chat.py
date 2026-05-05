# backend/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os, shutil, uuid
from backend.database.db import get_db
from backend.models.user import User
from backend.models.agreement import Agreement
from backend.models.message import Message
from backend.schemas.agreement_schema import MessageCreate, MessageResponse
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])
CHAT_UPLOAD_DIR = "uploads/chat"
os.makedirs(CHAT_UPLOAD_DIR, exist_ok=True)

def _check_access(agreement_id, current_user, db):
    ag = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not ag: raise HTTPException(404, "Agreement not found")
    if ag.user_a_id != current_user.id and ag.user_b_id != current_user.id: raise HTTPException(403, "Access denied")
    return ag

def _msg_to_response(msg, db):
    sender = db.query(User).filter(User.id == msg.sender_id).first()
    return MessageResponse(id=msg.id, agreement_id=msg.agreement_id, sender_id=msg.sender_id,
        sender_name=sender.full_name if sender else "Unknown", content=msg.content,
        file_path=msg.file_path, file_type=msg.file_type, message_type=msg.message_type, created_at=msg.created_at)

@router.get("/{agreement_id}/messages", response_model=List[MessageResponse])
def get_messages(agreement_id: int, since_id: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_access(agreement_id, current_user, db)
    q = db.query(Message).filter(Message.agreement_id == agreement_id)
    if since_id > 0: q = q.filter(Message.id > since_id)
    return [_msg_to_response(m, db) for m in q.order_by(Message.created_at.asc()).all()]

@router.post("/{agreement_id}/messages", response_model=MessageResponse)
def send_message(agreement_id: int, msg_data: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = _check_access(agreement_id, current_user, db)
    if ag.status not in ["accepted", "completed"]: raise HTTPException(400, "Can only chat in accepted agreements")
    m = Message(agreement_id=agreement_id, sender_id=current_user.id, content=msg_data.content, message_type="text")
    db.add(m); db.commit(); db.refresh(m)
    return _msg_to_response(m, db)

@router.post("/{agreement_id}/upload", response_model=MessageResponse)
def upload_file(agreement_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = _check_access(agreement_id, current_user, db)
    if ag.status not in ["accepted", "completed"]: raise HTTPException(400, "Agreement must be accepted")
    allowed = {"image/jpeg": "image", "image/png": "image", "image/jpg": "image", "application/pdf": "pdf"}
    if file.content_type not in allowed: raise HTTPException(400, "Only JPEG, PNG, PDF allowed")
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    fpath = os.path.join(CHAT_UPLOAD_DIR, f"{uuid.uuid4()}.{ext}")
    with open(fpath, "wb") as buf: shutil.copyfileobj(file.file, buf)
    m = Message(agreement_id=agreement_id, sender_id=current_user.id, content=f"[File: {file.filename}]",
        file_path=fpath, file_type=allowed[file.content_type], message_type="file")
    db.add(m); db.commit(); db.refresh(m)
    return _msg_to_response(m, db) 
