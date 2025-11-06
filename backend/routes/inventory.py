from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/", response_model=schemas.Inventory)
def add_inventory_item(item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    """Add an item to user's inventory"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == item.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if item already exists in inventory
    existing_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == item.user_id,
        models.Inventory.item_name == item.item_name
    ).first()

    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    # Create new inventory entry
    db_item = models.Inventory(
        user_id=item.user_id,
        item_name=item.item_name,
        quantity=item.quantity
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{user_id}", response_model=list[schemas.Inventory])
def get_user_inventory(user_id: int, db: Session = Depends(get_db)):
    """Get all items in a user's inventory"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(models.Inventory).filter(models.Inventory.user_id == user_id).all()

@router.get("/{user_id}/{item_name}", response_model=schemas.Inventory)
def get_inventory_item(user_id: int, item_name: str, db: Session = Depends(get_db)):
    """Get a specific item from user's inventory"""
    item = db.query(models.Inventory).filter(
        models.Inventory.user_id == user_id,
        models.Inventory.item_name == item_name
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    return item

@router.put("/{inventory_id}", response_model=schemas.Inventory)
def update_inventory_item(inventory_id: int, update: schemas.InventoryUpdate, db: Session = Depends(get_db)):
    """Update quantity of an inventory item"""
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item.quantity = max(0, update.quantity)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{inventory_id}")
def delete_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Delete an inventory item"""
    item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    db.delete(item)
    db.commit()
    return {"message": "Inventory item deleted successfully"}
