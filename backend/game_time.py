import sys
import os
from datetime import datetime

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

# Constants
OLD_AGE_THRESHOLD = 48  # 4 Years (Stats halved here)
DEATH_AGE_THRESHOLD = 60 # 5 Years (Pet dies here)

def load_clock():
    """
    Returns a dictionary with ticks AND calendar time.
    """
    db = SessionLocal()
    try:
        pet = db.query(Pet).first()
        if pet:
            # print(f"Loading Game Time: Year {pet.game_year}, Day {pet.game_day}")
            # Safety check: If fields are None, default to 1
            return {
                "ticks": pet.tick_progress if pet.tick_progress else 0,
                "year": pet.game_year if pet.game_year else 1,
                "month": pet.game_month if pet.game_month else 1,
                "day": pet.game_day if pet.game_day else 1,
                "hour": pet.game_hour if pet.game_hour else 8
            }
        else:
            return {"ticks": 0, "year": 1, "month": 1, "day": 1, "hour": 8}
    except Exception as e:
        print(f"Error loading clock: {e}")
        return {"ticks": 0, "year": 1, "month": 1, "day": 1, "hour": 8}
    finally:
        db.close()

def save_clock(current_ticks, game_time_dict):
    """
    Saves ticks AND the visual calendar date.
    """
    db = SessionLocal()
    try:
        db.query(Pet).update({
            Pet.tick_progress: current_ticks,
            Pet.game_year: game_time_dict['year'],
            Pet.game_month: game_time_dict['month'],
            Pet.game_day: game_time_dict['day'],
            Pet.game_hour: game_time_dict['hour']
        })
        db.commit()
        print("Game time & Calendar saved successfully.")
    except Exception as e:
        print(f"Error saving clock: {e}")
        db.rollback()
    finally:
        db.close()

def inc_month():
    """
    Called by main.py when ticks reach limit.
    Returns: A list of names of pets that died this month.
    """
    print("In-Game Month Passing...")
    
    db = SessionLocal()
    dead_pet_names = []
    
    try:
        pets = db.query(Pet).all()
        
        for pet in pets:
            # 1. Reset Tick Progress
            pet.tick_progress = 0

            # 2. Age the pet
            pet.age_months += 1
            pet.age_days += 30 
            
            # --- OLD AGE LOGIC (Halve Stats) ---
            # We trigger this EXACTLY at month 48 so it only happens once.
            if pet.age_months == OLD_AGE_THRESHOLD:
                print(f"{pet.name} has become an elder! Stats are halved.")
                pet.speed = pet.speed // 2
                pet.endurance = pet.endurance // 2
                pet.strength = pet.strength // 2
                pet.intelligence = pet.intelligence // 2
            
            # 3. Hunger Logic
            if pet.hunger < 3:
                pet.hunger += 1
            
            if pet.hunger >= 3:
                pet.health -= 20
                pet.happiness -= 20
            
            # 4. Growth/Score Logic
            if pet.age_months >= 57: pet.points += 10
            elif pet.age_months >= 48: pet.points += 5
            elif pet.age_months >= 36: pet.points += 3
            elif pet.age_months >= 12: pet.points += 2
            elif pet.age_months >= 3: pet.points += 1

            # --- DEATH LOGIC ---
            if pet.health <= 0 or pet.age_months >= DEATH_AGE_THRESHOLD:
                print(f"Pet {pet.name} has passed away.")
                dead_pet_names.append(pet.name) # Add to list for frontend
                db.delete(pet)
                continue 

            # 5. Safety Clamps
            pet.health = max(0, min(100, pet.health))
            pet.happiness = max(0, min(100, pet.happiness))
            pet.cleanliness = max(0, min(100, pet.cleanliness))
            pet.hunger = max(0, min(3, pet.hunger))

        db.commit()
        print("Month update complete. Database saved.")
        return dead_pet_names

    except Exception as e:
        print(f"Error during month update: {e}")
        db.rollback()
        return []
    finally:
        db.close()