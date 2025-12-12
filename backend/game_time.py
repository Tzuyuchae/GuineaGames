import sys
import os

# --- SMART IMPORTS ---
try:
    from backend.db_connect import SessionLocal
    from backend.models import Pet
except ImportError:
    try:
        from db_connect import SessionLocal
        from models import Pet
    except ImportError:
        print("CRITICAL ERROR: Could not import database connection in game_time.py")

def inc_month():
    """
    Called by main.py every 5 minutes (300 ticks).
    Uses SQLAlchemy to load pets, age them, and save changes.
    """
    print("In-Game Month Passing...")
    
    db = SessionLocal()
    
    try:
        pets = db.query(Pet).all()
        
        for pet in pets:
            # 1. Age the pet
            pet.age_months += 1
            
            # --- FIX: Sync Days with Months ---
            # Adding 30 days ensures they become "Adults" (age_days >= 1)
            # automatically when the month changes.
            pet.age_days += 30
            
            # 2. INCREASE HUNGER
            if pet.hunger < 3:
                pet.hunger += 1
            
            # 3. Apply Starvation Penalties
            if pet.hunger >= 3:
                pet.health -= 20
                pet.happiness -= 20
            
            # 4. Old Age Stat Decay
            if pet.age_months == 57:
                pet.speed = max(0, pet.speed - 10)
                pet.endurance = max(0, pet.endurance - 10)
            
            # 5. Growth/Score Logic
            if pet.age_months >= 57:
                pet.points += 10
            elif pet.age_months >= 48:
                pet.points += 5
            elif pet.age_months >= 36:
                pet.points += 3
            elif pet.age_months >= 12:
                pet.points += 2
            elif pet.age_months >= 3:
                pet.points += 1

            # 6. Death Logic
            if pet.health <= 0 or pet.age_months >= 60:
                print(f"Pet {pet.name} has passed away.")
                db.delete(pet)
                continue 

            # 7. Safety Clamps
            pet.health = max(0, min(100, pet.health))
            pet.happiness = max(0, min(100, pet.happiness))
            pet.cleanliness = max(0, min(100, pet.cleanliness))
            pet.hunger = max(0, min(3, pet.hunger))

        db.commit()
        print("Month update complete. Database saved.")

    except Exception as e:
        print(f"Error during month update: {e}")
        db.rollback()
    finally:
        db.close()