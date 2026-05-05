# backend/schemas/agreement_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class AgreementCreate(BaseModel):
    user_b_id: int
    user_a_teaches: str
    user_b_teaches: str
    hours_per_side: float = 1.0
    total_sessions: int = 1
    notes: Optional[str] = None

    @validator("hours_per_side")
    def hours_positive(cls, v):
        if v <= 0:
            raise ValueError("Hours must be positive")
        return v

class AgreementUpdate(BaseModel):
    status: str

    @validator("status")
    def valid_status(cls, v):
        if v not in ["accepted", "completed", "cancelled"]:
            raise ValueError("Status must be: accepted, completed, or cancelled")
        return v

class AgreementSessionUpdate(BaseModel):
    sessions_completed: int

class AgreementResponse(BaseModel):
    id: int
    user_a_id: int
    user_b_id: int
    user_a_name: str
    user_b_name: str
    user_a_teaches: str
    user_b_teaches: str
    hours_per_side: float
    status: str
    notes: Optional[str]
    sessions_completed: int
    total_sessions: int
    created_at: datetime
    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    agreement_id: int
    sender_id: int
    sender_name: str
    content: Optional[str]
    file_path: Optional[str]
    file_type: Optional[str]
    message_type: str
    created_at: datetime
    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    rated_user_id: int
    stars: float
    comment: Optional[str] = None

    @validator("stars")
    def stars_range(cls, v):
        if not (1.0 <= v <= 5.0):
            raise ValueError("Stars must be between 1 and 5")
        return v

class RatingResponse(BaseModel):
    id: int
    agreement_id: int
    rater_id: int
    rated_user_id: int
    stars: float
    comment: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True 
