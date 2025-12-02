from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import json
import datetime

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.post("/", response_model=schemas.Pet, status_code=status.HTTP_201_CREATED)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    """
    Create a new pet for a given owner.
    We initialize some reasonable default stats; you can tune these.
    """
    # Optional: verify owner exists
    owner = db.query(models.User).filter(models.User.id == pet.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    now = datetime.datetime.utcnow()

    db_pet = models.Pet(
        name=pet.name,
        species=pet.species,
        color=pet.color,
        owner_id=pet.owner_id,
        age_days=0,
        health=100,
        happiness=100,
        hunger=0,
        cleanliness=100,
        points=0,
        genetic_code=None,
        speed=5,
        endurance=5,
        last_updated=now,
    )

    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@router.get("/", response_model=list[schemas.Pet])
def get_all_pets(db: Session = Depends(get_db)):
    """Get all pets"""
    return db.query(models.Pet).all()

@router.get("/{pet_id}", response_model=schemas.Pet)
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    """Get a specific pet by ID"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet

@router.get("/owner/{owner_id}", response_model=list[schemas.Pet])
def get_pets_by_owner(owner_id: int, db: Session = Depends(get_db)):
    """Get all pets owned by a specific user"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(models.Pet).filter(models.Pet.owner_id == owner_id).all()

@router.put("/{pet_id}", response_model=schemas.Pet)
def update_pet(pet_id: int, pet_update: schemas.PetUpdate, db: Session = Depends(get_db)):
    """Update a pet's stats"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    if pet_update.name is not None:
        pet.name = pet_update.name
    if pet_update.health is not None:
        pet.health = max(0, min(100, pet_update.health))
    if pet_update.happiness is not None:
        pet.happiness = max(0, min(100, pet_update.happiness))
    if pet_update.hunger is not None:
        pet.hunger = max(0, min(3, pet_update.hunger))
    if pet_update.cleanliness is not None:
        pet.cleanliness = max(0, min(100, pet_update.cleanliness))

    db.commit()
    db.refresh(pet)
    return pet

@router.post("/{pet_id}/feed", response_model=schemas.Pet)
def feed_pet(pet_id: int, feed_request: schemas.FeedPetRequest, db: Session = Depends(get_db)):
    """
    Feed a pet with food from user's inventory.
    Decreases inventory quantity, updates pet stats, logs transaction.
    """
    # 1. Verify pet exists
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # 2. Check inventory for food item
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == pet.owner_id,
        models.Inventory.item_name == feed_request.item_name
    ).first()

    if not inventory_item or inventory_item.quantity < 1:
        raise HTTPException(status_code=400, detail="Food item not in inventory")

    # 3. Get food item details from shop
    shop_item = db.query(models.ShopItem).filter(
        models.ShopItem.name == feed_request.item_name,
        models.ShopItem.category == 'food'
    ).first()

    if not shop_item:
        raise HTTPException(status_code=400, detail="Item is not food")

    # 4. Parse effects and apply to pet
    try:
        effects = json.loads(shop_item.effect) if shop_item.effect else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid food effect data")

    # Apply effects with bounds checking
    if 'hunger' in effects:
        pet.hunger = min(3, pet.hunger + effects['hunger'])  # Max hunger is 3
    if 'health' in effects:
        pet.health = min(100, max(0, pet.health + effects['health']))
    if 'happiness' in effects:
        pet.happiness = min(100, max(0, pet.happiness + effects['happiness']))
    if 'cleanliness' in effects:
        pet.cleanliness = min(100, max(0, pet.cleanliness + effects['cleanliness']))

    pet.last_updated = datetime.datetime.utcnow()

    # 5. Decrease inventory quantity
    inventory_item.quantity -= 1
    if inventory_item.quantity == 0:
        db.delete(inventory_item)

    # 6. Log transaction
    transaction = models.Transaction(
        user_id=pet.owner_id,
        type="pet_feed",
        amount=0,  # No currency involved
        description=f"Fed {pet.name} with {feed_request.item_name}"
    )
    db.add(transaction)

    # 7. Commit all changes
    db.commit()
    db.refresh(pet)

    return pet

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    """Delete a pet"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}
