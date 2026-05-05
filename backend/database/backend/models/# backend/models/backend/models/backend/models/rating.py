# backend/models/rating.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("agreements.id"), nullable=False)
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rated_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stars = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    agreement = relationship("Agreement", back_populates="ratings")
    rater = relationship("User", foreign_keys=[rater_id], back_populates="ratings_given")
    rated_user = relationship("User", foreign_keys=[rated_user_id], back_populates="ratings_received") 
