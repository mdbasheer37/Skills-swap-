# backend/models/agreement.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base

class Agreement(Base):
    __tablename__ = "agreements"
    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_a_teaches = Column(String(200), nullable=False)
    user_b_teaches = Column(String(200), nullable=False)
    hours_per_side = Column(Float, default=1.0)
    status = Column(String(20), default="pending")
    notes = Column(Text, nullable=True)
    sessions_completed = Column(Integer, default=0)
    total_sessions = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    user_a = relationship("User", foreign_keys=[user_a_id], back_populates="agreements_as_user_a")
    user_b = relationship("User", foreign_keys=[user_b_id], back_populates="agreements_as_user_b")
    messages = relationship("Message", back_populates="agreement")
    ratings = relationship("Rating", back_populates="agreement") 
