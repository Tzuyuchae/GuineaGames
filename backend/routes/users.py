from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import get_db


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a user if the email is new; if the email already exists,
    return the existing user instead of crashing on UNIQUE constraint.
    """
    # See if a user with this email already exists
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        return existing

    # For this project, it's fine to store the raw password as password_hash
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password,
        balance=0,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        # Double-check for an existing user
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            return existing

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )
