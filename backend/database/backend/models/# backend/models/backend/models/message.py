# backend/models/message.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("agreements.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    file_type = Column(String(20), nullable=True)
    message_type = Column(String(10), default="text")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    agreement = relationship("Agreement", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent") 
