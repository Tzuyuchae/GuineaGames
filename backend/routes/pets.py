from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import json
import datetime
from typing import List

# Add these imports at the top of the file
from genetics import GeneticCode, BreedingEngine
from pricing import RarityCalculator

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.post("/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    """Create a new pet for a user with auto-generated genetics"""
    user = db.query(models.User).filter(models.User.id == pet.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_pet = models.Pet(
        owner_id=pet.owner_id,
        name=pet.name,
        species=pet.species,
        color=pet.color,
        health=100,
        happiness=100,
        hunger=0,
        cleanliness=100
    )
    
    db_pet.genetic_code = GeneticCode.generate_random_genetic_code(db)
    
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)

    if db_pet.genetic_code:
        genes_map = GeneticCode.decode(db_pet.genetic_code)
        for gene_name, (a1_sym, a2_sym) in genes_map.items():
            gene = db.query(models.Gene).filter(models.Gene.name == gene_name).first()
            if gene:
                a1 = db.query(models.Allele).filter(models.Allele.gene_id == gene.id, models.Allele.symbol == a1_sym).first()
                a2 = db.query(models.Allele).filter(models.Allele.gene_id == gene.id, models.Allele.symbol == a2_sym).first()
                if a1 and a2:
                    pg = models.PetGenetics(
                        pet_id=db_pet.id,
                        gene_id=gene.id,
                        allele1_id=a1.id,
                        allele2_id=a2.id
                    )
                    db.add(pg)
        db.commit()

    BreedingEngine.update_stats_from_genetics(db, db_pet)
    RarityCalculator.calculate_and_store_valuation(db_pet, db)

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
    user = db.query(models.User).filter(models.User.id == owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(models.Pet).filter(models.Pet.owner_id == owner_id).all()

@router.put("/{pet_id}", response_model=schemas.Pet)
def update_pet(pet_id: int, pet_update: schemas.PetUpdate, db: Session = Depends(get_db)):
    """Update a pet's stats AND name"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # --- FIX: Explicitly handle the name update ---
    if pet_update.name is not None:
        pet.name = pet_update.name

    # Handle other stats
    if pet_update.health is not None:
        pet.health = max(0, min(100, pet_update.health))
    if pet_update.happiness is not None:
        pet.happiness = max(0, min(100, pet_update.happiness))
    if pet_update.hunger is not None:
        pet.hunger = max(0, min(3, pet_update.hunger))
    if pet_update.cleanliness is not None:
        pet.cleanliness = max(0, min(100, pet_update.cleanliness))
    
    # Handle age (for the GROW button)
    if pet_update.age_days is not None:
        pet.age_days = pet_update.age_days

    pet.last_updated = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(pet)
    return pet

@router.post("/{pet_id}/feed", response_model=schemas.Pet)
def feed_pet(pet_id: int, feed_request: schemas.FeedPetRequest, db: Session = Depends(get_db)):
    """Feed a pet with food from user's inventory"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Check inventory
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == pet.owner_id,
        models.Inventory.item_name == feed_request.item_name
    ).first()

    if not inventory_item or inventory_item.quantity < 1:
        raise HTTPException(status_code=400, detail="Food item not in inventory")

    shop_item = db.query(models.ShopItem).filter(
        models.ShopItem.name == feed_request.item_name
    ).first()

    if not shop_item:
        # Fallback if item isn't in shop database but exists in inventory
        effects = {"hunger": 1, "happiness": 5}
    else:
        try:
            effects = json.loads(shop_item.effect) if shop_item.effect else {}
        except json.JSONDecodeError:
            effects = {}

    # Apply effects
    # Hunger: Reduce value (min 0)
    if 'hunger' in effects:
        pet.hunger = max(0, pet.hunger - effects['hunger'])
    
    # Health/Happiness: Increase value (max 100)
    if 'health' in effects:
        pet.health = min(100, max(0, pet.health + effects['health']))
    if 'happiness' in effects:
        pet.happiness = min(100, max(0, pet.happiness + effects['happiness']))
    if 'cleanliness' in effects:
        pet.cleanliness = min(100, max(0, pet.cleanliness + effects['cleanliness']))

    pet.last_updated = datetime.datetime.utcnow()

    # Decrease inventory
    inventory_item.quantity -= 1
    if inventory_item.quantity == 0:
        db.delete(inventory_item)

    # Log transaction
    transaction = models.Transaction(
        user_id=pet.owner_id,
        type="pet_feed",
        amount=0,
        description=f"Fed {pet.name} with {feed_request.item_name}"
    )
    db.add(transaction)

    db.commit()
    db.refresh(pet)
    return pet

@router.post("/decay/{user_id}")
def process_daily_decay(user_id: int, db: Session = Depends(get_db)):
    """
    Called by the frontend clock. 
    Increases hunger. Decreases health if starving. Handles Death.
    """
    pets = db.query(models.Pet).filter(models.Pet.owner_id == user_id).all()
    results = {"dead_pets": [], "starving_pets": []}

    for pet in pets:
        # 1. Increase Hunger
        # If not already at max hunger (3), they get hungrier
        if pet.hunger < 3:
            pet.hunger += 1
        
        # 2. Apply Starvation Damage
        # If they were already at max hunger (or just reached it), they take damage
        if pet.hunger == 3:
            pet.health -= 25  # dies in 4 days of starvation
            pet.happiness -= 20
            results["starving_pets"].append(pet.name)

        # 3. Check for Death
        if pet.health <= 0:
            results["dead_pets"].append(pet.name)
            db.delete(pet) # Bye bye birdie
        else:
            # Clamp values
            pet.health = max(0, pet.health)
            pet.happiness = max(0, pet.happiness)

    db.commit()
    return results

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    """Delete a pet"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}