from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction record"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == transaction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_transaction = models.Transaction(
        user_id=transaction.user_id,
        type=transaction.type,
        amount=transaction.amount,
        description=transaction.description
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/user/{user_id}", response_model=list[schemas.Transaction])
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    """Get all transactions for a user"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()

@router.get("/{transaction_id}", response_model=schemas.Transaction)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.get("/user/{user_id}/type/{transaction_type}", response_model=list[schemas.Transaction])
def get_transactions_by_type(user_id: int, transaction_type: str, db: Session = Depends(get_db)):
    """Get all transactions of a specific type for a user"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == transaction_type
    ).all()
