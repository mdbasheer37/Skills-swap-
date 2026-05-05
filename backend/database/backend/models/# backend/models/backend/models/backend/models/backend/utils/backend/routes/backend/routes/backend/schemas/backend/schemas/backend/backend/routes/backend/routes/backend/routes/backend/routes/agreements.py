# backend/routes/agreements.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database.db import get_db
from backend.models.user import User
from backend.models.agreement import Agreement
from backend.schemas.agreement_schema import AgreementCreate, AgreementUpdate, AgreementResponse, AgreementSessionUpdate
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/agreements", tags=["Agreements"])

def _build_response(agreement, db):
    user_a = db.query(User).filter(User.id == agreement.user_a_id).first()
    user_b = db.query(User).filter(User.id == agreement.user_b_id).first()
    return AgreementResponse(
        id=agreement.id, user_a_id=agreement.user_a_id, user_b_id=agreement.user_b_id,
        user_a_name=user_a.full_name if user_a else "Unknown",
        user_b_name=user_b.full_name if user_b else "Unknown",
        user_a_teaches=agreement.user_a_teaches, user_b_teaches=agreement.user_b_teaches,
        hours_per_side=agreement.hours_per_side, status=agreement.status,
        notes=agreement.notes, sessions_completed=agreement.sessions_completed,
        total_sessions=agreement.total_sessions, created_at=agreement.created_at,
        accepted_at=agreement.accepted_at, completed_at=agreement.completed_at,
    )

@router.post("/", response_model=AgreementResponse, status_code=201)
def create_agreement(data: AgreementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    other_user = db.query(User).filter(User.id == data.user_b_id).first()
    if not other_user: raise HTTPException(404, "User not found")
    if other_user.id == current_user.id: raise HTTPException(400, "Cannot create agreement with yourself")
    ag = Agreement(user_a_id=current_user.id, user_b_id=data.user_b_id,
        user_a_teaches=data.user_a_teaches, user_b_teaches=data.user_b_teaches,
        hours_per_side=data.hours_per_side, total_sessions=data.total_sessions, notes=data.notes, status="pending")
    db.add(ag); db.commit(); db.refresh(ag)
    return _build_response(ag, db)

@router.get("/", response_model=List[AgreementResponse])
def get_my_agreements(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ags = db.query(Agreement).filter((Agreement.user_a_id == current_user.id) | (Agreement.user_b_id == current_user.id)).order_by(Agreement.created_at.desc()).all()
    return [_build_response(a, db) for a in ags]

@router.get("/{agreement_id}", response_model=AgreementResponse)
def get_agreement(agreement_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not ag: raise HTTPException(404, "Agreement not found")
    if ag.user_a_id != current_user.id and ag.user_b_id != current_user.id: raise HTTPException(403, "Access denied")
    return _build_response(ag, db)

@router.put("/{agreement_id}/status", response_model=AgreementResponse)
def update_agreement_status(agreement_id: int, update: AgreementUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not ag: raise HTTPException(404, "Agreement not found")
    if ag.user_a_id != current_user.id and ag.user_b_id != current_user.id: raise HTTPException(403, "Access denied")
    if update.status == "accepted" and ag.user_b_id != current_user.id: raise HTTPException(403, "Only the invited user can accept")
    ag.status = update.status
    if update.status == "accepted": ag.accepted_at = datetime.utcnow()
    elif update.status == "completed": ag.completed_at = datetime.utcnow()
    db.commit(); db.refresh(ag)
    return _build_response(ag, db)

@router.put("/{agreement_id}/sessions", response_model=AgreementResponse)
def update_sessions(agreement_id: int, update: AgreementSessionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not ag: raise HTTPException(404, "Agreement not found")
    if ag.user_a_id != current_user.id and ag.user_b_id != current_user.id: raise HTTPException(403, "Access denied")
    if update.sessions_completed > ag.total_sessions: raise HTTPException(400, "Cannot exceed total sessions")
    ag.sessions_completed = update.sessions_completed
    if ag.sessions_completed >= ag.total_sessions:
        ag.status = "completed"; ag.completed_at = datetime.utcnow()
    db.commit(); db.refresh(ag)
    return _build_response(ag, db) 
