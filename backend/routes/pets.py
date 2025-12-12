from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_connect import get_db
import models, schemas
import json
import datetime
from typing import List

# Add these imports at the top of the file
from genetics import GeneticCode, BreedingEngine
from pricing import RarityCalculator

# --- THIS LINE IS CRITICAL (It was missing in the broken version) ---
router = APIRouter(prefix="/pets", tags=["Pets"])

@router.post("/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    """Create a new pet and FORCE stats/phenotype/rarity to match request"""
    # 1. Verify User
    user = db.query(models.User).filter(models.User.id == pet.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Determine Visuals
    target_hair = "fluffy" if getattr(pet, 'coat_length', 'Short') == "Long" else "short"
    target_color = pet.color 

    db_pet = models.Pet(
        owner_id=pet.owner_id,
        name=pet.name,
        species=pet.species,
        color=pet.color,
        health=100,
        happiness=100,
        hunger=0,
        cleanliness=100,
        color_phenotype=target_color, 
        hair_type=target_hair,
        rarity_tier="Common", # Default
        market_value=0
    )
    
    # 3. Generate Genetics (Visual Match)
    best_genetic_code = None
    for _ in range(50):
        candidate = GeneticCode.generate_random_genetic_code(db)
        decoded = GeneticCode.decode(candidate)
        gene_color = decoded.get('coat_color', 'Mixed')
        gene_hair = decoded.get('hair_type', 'short')
        
        color_ok = (target_color in gene_color) or (target_color == "Orange" and "Mixed" in gene_color)
        hair_ok = (gene_hair == target_hair)
        
        if color_ok and hair_ok:
            best_genetic_code = candidate
            break
            
    db_pet.genetic_code = best_genetic_code if best_genetic_code else GeneticCode.generate_random_genetic_code(db)
    
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)

    # 4. Run Breeding Engine (Calculates baseline stats)
    BreedingEngine.update_stats_from_genetics(db, db_pet)
    
    # Force visuals again just in case
    db_pet.color_phenotype = target_color
    db_pet.hair_type = target_hair

    # 5. --- FIX: FORCE STATS AND CALCULATE RARITY MANUALLY ---
    if pet.speed is not None and pet.endurance is not None:
        # Apply Stats
        db_pet.speed = pet.speed
        db_pet.endurance = pet.endurance
        
        # Calculate Average Stat
        avg_stat = (db_pet.speed + db_pet.endurance) / 2
        
        # Force Rarity Tier based on the high stats
        if avg_stat >= 90:
            db_pet.rarity_tier = "Legendary"
            db_pet.rarity_score = 4
        elif avg_stat >= 75:
            db_pet.rarity_tier = "Rare"
            db_pet.rarity_score = 3
        elif avg_stat >= 60:
            db_pet.rarity_tier = "Uncommon"
            db_pet.rarity_score = 2
        else:
            db_pet.rarity_tier = "Common"
            db_pet.rarity_score = 1

        # Apply Price
        if pet.market_value is not None:
            db_pet.market_value = pet.market_value
            
    else:
        # If no forced stats (e.g. from Breeding), use standard calculator
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
        effects = {"hunger": 1, "happiness": 5}
    else:
        try:
            effects = json.loads(shop_item.effect) if shop_item.effect else {}
        except json.JSONDecodeError:
            effects = {}

    if 'hunger' in effects:
        pet.hunger = max(0, pet.hunger - effects['hunger'])
    
    if 'health' in effects:
        pet.health = min(100, max(0, pet.health + effects['health']))
    if 'happiness' in effects:
        pet.happiness = min(100, max(0, pet.happiness + effects['happiness']))
    if 'cleanliness' in effects:
        pet.cleanliness = min(100, max(0, pet.cleanliness + effects['cleanliness']))

    pet.last_updated = datetime.datetime.utcnow()

    inventory_item.quantity -= 1
    if inventory_item.quantity == 0:
        db.delete(inventory_item)

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
    Called by the frontend clock every game day (24 hours in-game).
    Responsible for:
    1. Aging pets (Growing up)
    2. Increasing hunger
    3. Decreasing health if starving
    4. Handling death
    """
    pets = db.query(models.Pet).filter(models.Pet.owner_id == user_id).all()
    results = {"dead_pets": [], "starving_pets": [], "aged_pets": 0}

    for pet in pets:
        # --- 1. AGE THE PET ---
        pet.age_days += 1
        results["aged_pets"] += 1

        # --- 2. INCREASE HUNGER ---
        # Hunger goes from 0 (Full) to 3 (Starving)
        if pet.hunger < 3:
            pet.hunger += 1
        
        # --- 3. APPLY PENALTIES ---
        if pet.hunger >= 3:
            # Starving penalties
            pet.health -= 25 
            pet.happiness -= 20
            results["starving_pets"].append(pet.name)
        elif pet.hunger == 2:
            # Hungry penalties
            pet.happiness -= 5
        
        # Cap stats
        pet.health = max(0, pet.health)
        pet.happiness = max(0, pet.happiness)

        # --- 4. CHECK DEATH ---
        if pet.health <= 0:
            pet.is_dead = True # Mark as dead (if you have this flag) or delete
            results["dead_pets"].append(pet.name)
            # db.delete(pet) # Uncomment if you want perma-death deletion immediately

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
@router.post("/cooldowns/tick/{user_id}")
def tick_cooldowns(user_id: int, seconds: int = 1, db: Session = Depends(get_db)):
    """
    Called by the frontend game loop to decrease breeding cooldowns.
    Only affects pets that currently have a cooldown > 0.
    """
    # Get pets with active cooldowns
    pets_on_cooldown = db.query(models.Pet).filter(
        models.Pet.owner_id == user_id, 
        models.Pet.breeding_cooldown > 0
    ).all()
    
    if not pets_on_cooldown:
        return {"message": "No updates needed"}

    for pet in pets_on_cooldown:
        # Decrease cooldown, stop at 0
        pet.breeding_cooldown = max(0, pet.breeding_cooldown - seconds)
    
    db.commit()
    return {"message": "Cooldowns updated", "updated_count": len(pets_on_cooldown)}
@router.post("/feed/all/{user_id}")
def feed_all_pets(user_id: int, db: Session = Depends(get_db)):
    """Feeds all hungry pets using available food in inventory."""
    
    # 1. Get all hungry pets
    pets = db.query(models.Pet).filter(
        models.Pet.owner_id == user_id,
        models.Pet.hunger > 0
    ).all()
    
    if not pets:
        return {"message": "No hungry pets!", "fed_count": 0}

    # 2. Get all food items
    # We filter by 'food' type or just assume items in inventory are usable
    inventory = db.query(models.Inventory).filter(models.Inventory.user_id == user_id).all()
    
    # Convert inventory to a mutable list we can decrement
    food_stack = []
    for item in inventory:
        # Simple logic: assume everything in inventory is food for now, 
        # or check a specific list if you have non-food items.
        if item.quantity > 0:
            food_stack.append(item)
            
    if not food_stack:
        return {"message": "No food in inventory!", "fed_count": 0}

    pets_fed = 0
    
    for pet in pets:
        while pet.hunger > 0 and food_stack:
            # Get the first available food item
            current_food = food_stack[0]
            
            # Feed Logic
            pet.hunger -= 1
            pet.happiness = min(100, pet.happiness + 5)
            pet.health = min(100, pet.health + 2)
            
            # Decrement Inventory
            current_food.quantity -= 1
            
            # If item runs out, remove from stack and delete from DB
            if current_food.quantity == 0:
                db.delete(current_food)
                food_stack.pop(0)
                
            pets_fed += 1

    db.commit()
    
    return {
        "message": f"Fed {pets_fed} times!",
        "fed_count": pets_fed,
        "remaining_food": sum(i.quantity for i in food_stack)
    }