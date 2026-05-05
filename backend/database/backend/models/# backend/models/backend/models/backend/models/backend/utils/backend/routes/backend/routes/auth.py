# backend/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database.db import get_db
from backend.models.user import User
from backend.schemas.user_schema import UserRegister, UserLogin, Token, UserResponse
from backend.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    if not user_data.email and not user_data.phone:
        raise HTTPException(400, "Either email or phone number is required")
    if user_data.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(400, "Email already registered")
    if user_data.phone:
        if db.query(User).filter(User.phone == user_data.phone).first():
            raise HTTPException(400, "Phone number already registered")
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password),
        language=user_data.language or "english"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    identifier = login_data.identifier.strip()
    user = None
    if "@" in identifier:
        user = db.query(User).filter(User.email == identifier).first()
    else:
        user = db.query(User).filter(User.phone == identifier).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid email/phone or password")
    if user.is_blocked:
        raise HTTPException(403, "Account blocked. Contact support.")
    user.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer", user_id=user.id, full_name=user.full_name)

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully. Please delete your token."} 
