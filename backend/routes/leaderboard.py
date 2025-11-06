from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
import models, schemas

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

def update_leaderboard_ranks(db: Session):
    """Update all leaderboard ranks based on scores"""
    leaderboard_entries = db.query(models.Leaderboard).order_by(desc(models.Leaderboard.score)).all()
    for rank, entry in enumerate(leaderboard_entries, 1):
        entry.rank = rank
    db.commit()

@router.post("/", response_model=schemas.Leaderboard)
def create_leaderboard_entry(entry: schemas.LeaderboardCreate, db: Session = Depends(get_db)):
    """Create or update a leaderboard entry for a user"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user already has a leaderboard entry
    existing_entry = db.query(models.Leaderboard).filter(models.Leaderboard.user_id == entry.user_id).first()
    if existing_entry:
        existing_entry.score = entry.score
        db.commit()
        db.refresh(existing_entry)
    else:
        db_entry = models.Leaderboard(
            user_id=entry.user_id,
            score=entry.score
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        existing_entry = db_entry

    # Update all ranks
    update_leaderboard_ranks(db)
    db.refresh(existing_entry)
    return existing_entry

@router.get("/", response_model=list[schemas.Leaderboard])
def get_leaderboard(limit: int = 100, db: Session = Depends(get_db)):
    """Get the complete leaderboard sorted by rank"""
    return db.query(models.Leaderboard).order_by(models.Leaderboard.rank).limit(limit).all()

@router.get("/top/{limit}", response_model=list[schemas.Leaderboard])
def get_top_players(limit: int = 10, db: Session = Depends(get_db)):
    """Get top N players"""
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be positive")
    return db.query(models.Leaderboard).order_by(models.Leaderboard.rank).limit(limit).all()

@router.get("/user/{user_id}", response_model=schemas.Leaderboard)
def get_user_rank(user_id: int, db: Session = Depends(get_db)):
    """Get a user's leaderboard entry and rank"""
    entry = db.query(models.Leaderboard).filter(models.Leaderboard.user_id == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="User not found on leaderboard")
    return entry

@router.put("/user/{user_id}", response_model=schemas.Leaderboard)
def update_user_score(user_id: int, score_update: int, db: Session = Depends(get_db)):
    """Update a user's score (add to existing score)"""
    entry = db.query(models.Leaderboard).filter(models.Leaderboard.user_id == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="User not found on leaderboard")

    entry.score += score_update
    db.commit()
    db.refresh(entry)

    # Update all ranks
    update_leaderboard_ranks(db)
    db.refresh(entry)
    return entry

@router.delete("/user/{user_id}")
def remove_from_leaderboard(user_id: int, db: Session = Depends(get_db)):
    """Remove a user from the leaderboard"""
    entry = db.query(models.Leaderboard).filter(models.Leaderboard.user_id == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="User not found on leaderboard")

    db.delete(entry)
    db.commit()

    # Update all ranks
    update_leaderboard_ranks(db)
    return {"message": "User removed from leaderboard"}
