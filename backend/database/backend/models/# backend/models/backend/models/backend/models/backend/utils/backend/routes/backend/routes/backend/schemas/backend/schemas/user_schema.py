# backend/schemas/user_schema.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    language: Optional[str] = "english"

    @validator("password")
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class UserLogin(BaseModel):
    identifier: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    skills_to_teach: Optional[str] = None
    skills_to_learn: Optional[str] = None
    skill_level: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    language: str
    location: Optional[str]
    profile_photo: Optional[str]
    skills_to_teach: Optional[str]
    skills_to_learn: Optional[str]
    skill_level: str
    trust_score: float
    total_ratings: int
    is_active: bool
    is_blocked: bool
    created_at: datetime
    class Config:
        from_attributes = True

class MatchResponse(BaseModel):
    user: UserResponse
    match_score: int
    matching_skills: List[str]

class AdminUserSummary(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    trust_score: float
    is_active: bool
    is_blocked: bool
    created_at: datetime
    class Config:
        from_attributes = True 
