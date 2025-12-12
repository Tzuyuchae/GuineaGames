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

def load_clock():
    """
    Returns a dictionary with ticks AND calendar time.
    """
    db = SessionLocal()
    try:
        pet = db.query(Pet).first()
        if pet:
            print(f"Loading Game Time: Year {pet.game_year}, Day {pet.game_day}")
            return {
                "ticks": pet.tick_progress,
                "year": pet.game_year,
                "month": pet.game_month,
                "day": pet.game_day,
                "hour": pet.game_hour
            }
        else:
            # Default start time
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
        # Update ALL pets with the global time data
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
    Called by main.py when ticks reach 300 (5 minutes).
    Ages pets and RESETS the saved tick progress to 0.
    """
    print("In-Game Month Passing...")
    
    db = SessionLocal()
    
    try:
        pets = db.query(Pet).all()
        
        for pet in pets:
            # --- RESET CLOCK ---
            # The month has rolled over, so progress resets to 0
            pet.tick_progress = 0

            # 1. Age the pet
            pet.age_months += 1
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