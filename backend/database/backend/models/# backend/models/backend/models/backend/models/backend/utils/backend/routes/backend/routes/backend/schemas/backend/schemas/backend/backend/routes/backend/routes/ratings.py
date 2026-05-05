# backend/routes/ratings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.db import get_db
from backend.models.user import User
from backend.models.agreement import Agreement
from backend.models.rating import Rating
from backend.schemas.agreement_schema import RatingCreate, RatingResponse
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/ratings", tags=["Ratings"])

def _recalculate_trust(user, db):
    ratings = db.query(Rating).filter(Rating.rated_user_id == user.id).all()
    if ratings:
        user.trust_score = round(sum(r.stars for r in ratings) / len(ratings), 2)
        user.total_ratings = len(ratings)
    else:
        user.trust_score = 0.0; user.total_ratings = 0
    db.commit()

@router.post("/{agreement_id}", response_model=RatingResponse, status_code=201)
def submit_rating(agreement_id: int, rating_data: RatingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ag = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not ag: raise HTTPException(404, "Agreement not found")
    if ag.user_a_id != current_user.id and ag.user_b_id != current_user.id: raise HTTPException(403, "Access denied")
    if ag.status != "completed": raise HTTPException(400, "Can only rate completed agreements")
    other_id = ag.user_b_id if ag.user_a_id == current_user.id else ag.user_a_id
    if rating_data.rated_user_id != other_id: raise HTTPException(400, "You can only rate the other participant")
    if db.query(Rating).filter(Rating.agreement_id == agreement_id, Rating.rater_id == current_user.id).first():
        raise HTTPException(400, "You already rated this exchange")
    rated_user = db.query(User).filter(User.id == rating_data.rated_user_id).first()
    if not rated_user: raise HTTPException(404, "User not found")
    r = Rating(agreement_id=agreement_id, rater_id=current_user.id, rated_user_id=rating_data.rated_user_id, stars=rating_data.stars, comment=rating_data.comment)
    db.add(r); db.commit()
    _recalculate_trust(rated_user, db)
    db.refresh(r)
    return r

@router.get("/user/{user_id}", response_model=List[RatingResponse])
def get_user_ratings(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not db.query(User).filter(User.id == user_id).first(): raise HTTPException(404, "User not found")
    return db.query(Rating).filter(Rating.rated_user_id == user_id).all() 
