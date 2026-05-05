# backend/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os, shutil, uuid
from backend.database.db import get_db
from backend.models.user import User
from backend.schemas.user_schema import UserResponse, UserProfileUpdate, MatchResponse
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
UPLOAD_DIR = "uploads/profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/match/find", response_model=List[MatchResponse])
def find_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    my_teach = current_user.get_teach_skills_list()
    my_learn = current_user.get_learn_skills_list()
    if not my_teach and not my_learn:
        raise HTTPException(400, "Please set your skills to teach and learn first")
    other_users = db.query(User).filter(User.id != current_user.id, User.is_active == True, User.is_blocked == False).all()
    matches = []
    for other in other_users:
        other_teach = other.get_teach_skills_list()
        other_learn = other.get_learn_skills_list()
        matching_skills = []
        for skill in my_learn:
            for ts in other_teach:
                if skill.lower() == ts.lower():
                    matching_skills.append(f"They teach: {ts}")
        for skill in my_teach:
            for tw in other_learn:
                if skill.lower() == tw.lower():
                    matching_skills.append(f"They want: {tw}")
        if matching_skills:
            matches.append(MatchResponse(user=UserResponse.model_validate(other), match_score=len(matching_skills), matching_skills=matching_skills))
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches[:20]

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_my_profile(update_data: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if update_data.full_name is not None: current_user.full_name = update_data.full_name
    if update_data.bio is not None: current_user.bio = update_data.bio
    if update_data.location is not None: current_user.location = update_data.location
    if update_data.language is not None:
        if update_data.language not in ["english", "hausa"]: raise HTTPException(400, "Language must be english or hausa")
        current_user.language = update_data.language
    if update_data.skills_to_teach is not None: current_user.skills_to_teach = update_data.skills_to_teach
    if update_data.skills_to_learn is not None: current_user.skills_to_learn = update_data.skills_to_learn
    if update_data.skill_level is not None:
        if update_data.skill_level not in ["beginner","intermediate","expert"]: raise HTTPException(400, "Invalid skill level")
        current_user.skill_level = update_data.skill_level
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user: raise HTTPException(404, "User not found")
    return user
