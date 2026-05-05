# backend/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.user import User
from backend.models.agreement import Agreement
from backend.schemas.user_schema import AdminUserSummary
from backend.utils.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[AdminUserSummary])
def list_all_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()

@router.post("/users/{user_id}/block")
def block_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    if user.is_admin: raise HTTPException(400, "Cannot block an admin")
    user.is_blocked = True; db.commit()
    return {"message": f"User {user.full_name} blocked"}

@router.post("/users/{user_id}/unblock")
def unblock_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    user.is_blocked = False; db.commit()
    return {"message": f"User {user.full_name} unblocked"}

@router.get("/agreements")
def list_all_agreements(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    ags = db.query(Agreement).order_by(Agreement.created_at.desc()).all()
    result = []
    for ag in ags:
        ua = db.query(User).filter(User.id == ag.user_a_id).first()
        ub = db.query(User).filter(User.id == ag.user_b_id).first()
        result.append({"id": ag.id, "user_a": ua.full_name if ua else "?", "user_b": ub.full_name if ub else "?",
            "user_a_teaches": ag.user_a_teaches, "user_b_teaches": ag.user_b_teaches,
            "status": ag.status, "sessions_completed": ag.sessions_completed, "total_sessions": ag.total_sessions})
    return result

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return {
        "users": {"total": db.query(User).count(), "active": db.query(User).filter(User.is_active==True, User.is_blocked==False).count(), "blocked": db.query(User).filter(User.is_blocked==True).count()},
        "agreements": {"total": db.query(Agreement).count(), "pending": db.query(Agreement).filter(Agreement.status=="pending").count(), "active": db.query(Agreement).filter(Agreement.status=="accepted").count(), "completed": db.query(Agreement).filter(Agreement.status=="completed").count()}
    } 
