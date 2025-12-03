from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import json
import datetime
# Add these imports at the top of the file
from genetics import GeneticCode, BreedingEngine
from pricing import RarityCalculator

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.post("/", response_model=schemas.Pet)
def create_pet(pet: schemas.PetCreate, db: Session = Depends(get_db)):
    """Create a new pet for a user with auto-generated genetics"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == pet.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Create basic pet object
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
    
    # 2. Generate Random Genetics
    db_pet.genetic_code = GeneticCode.generate_random_genetic_code(db)
    
    # 3. Add to DB
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)

    # 4. Parse genetic code and create PetGenetics records
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

    # 5. Calculate Stats & Value
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
    
    # --- ADDED AGE UPDATE ---
    if pet_update.age_days is not None:
        pet.age_days = pet_update.age_days

    db.commit()
    db.refresh(pet)
    return pet

@router.post("/{pet_id}/feed", response_model=schemas.Pet)
def feed_pet(pet_id: int, feed_request: schemas.FeedPetRequest, db: Session = Depends(get_db)):
    """Feed a pet with food from user's inventory"""
    # 1. Verify pet exists
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # 2. Check inventory
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.user_id == pet.owner_id,
        models.Inventory.item_name == feed_request.item_name
    ).first()

    if not inventory_item or inventory_item.quantity < 1:
        raise HTTPException(status_code=400, detail="Food item not in inventory")

    # 3. Get food item details
    shop_item = db.query(models.ShopItem).filter(
        models.ShopItem.name == feed_request.item_name,
        models.ShopItem.category == 'food'
    ).first()

    if not shop_item:
        raise HTTPException(status_code=400, detail="Item is not food")

    # 4. Parse effects
    try:
        effects = json.loads(shop_item.effect) if shop_item.effect else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid food effect data")

    # Apply effects
    if 'hunger' in effects:
        pet.hunger = min(3, pet.hunger + effects['hunger'])
    if 'health' in effects:
        pet.health = min(100, max(0, pet.health + effects['health']))
    if 'happiness' in effects:
        pet.happiness = min(100, max(0, pet.happiness + effects['happiness']))
    if 'cleanliness' in effects:
        pet.cleanliness = min(100, max(0, pet.cleanliness + effects['cleanliness']))

    pet.last_updated = datetime.datetime.utcnow()

    # 5. Decrease inventory
    inventory_item.quantity -= 1
    if inventory_item.quantity == 0:
        db.delete(inventory_item)

    # 6. Log transaction
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

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db)):
    """Delete a pet"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}