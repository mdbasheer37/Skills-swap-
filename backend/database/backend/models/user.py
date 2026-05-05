# backend/models/user.py 
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    language = Column(String(10), default="english")
    location = Column(String(100), nullable=True)
    profile_photo = Column(String(255), nullable=True)
    skills_to_teach = Column(Text, nullable=True)
    skills_to_learn = Column(Text, nullable=True)
    skill_level = Column(String(20), default="beginner")
    trust_score = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    agreements_as_user_a = relationship("Agreement", foreign_keys="Agreement.user_a_id", back_populates="user_a")
    agreements_as_user_b = relationship("Agreement", foreign_keys="Agreement.user_b_id", back_populates="user_b")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    ratings_given = relationship("Rating", foreign_keys="Rating.rater_id", back_populates="rater")
    ratings_received = relationship("Rating", foreign_keys="Rating.rated_user_id", back_populates="rated_user")

    def get_teach_skills_list(self):
        if self.skills_to_teach:
            return [s.strip() for s in self.skills_to_teach.split(",") if s.strip()]
        return []

    def get_learn_skills_list(self):
        if self.skills_to_learn:
            return [s.strip() for s in self.skills_to_learn.split(",") if s.strip()]
        return [] 
