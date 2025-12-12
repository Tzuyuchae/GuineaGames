"""
- # NOTE: Update pets.py to import and use feeding.py's apply_food_item_to_pet for feeding logic.

Feeding system for Guinea Games.

Responsibilities:
- Apply food effects (from SHOP_ITEMS.effect JSON) to a pet.
- Use user inventory to feed pets.
- Auto-feed hungry guinea pigs, prioritizing highest hunger first.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
import datetime
import json

import models


# Utility helpers
def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp integer between min_val and max_val."""
    return max(min_val, min(max_val, value))


def parse_food_effect(shop_item: models.ShopItem) -> Dict[str, int]:
    """
    Parse the JSON 'effect' field from a ShopItem into a dict.

    Expected keys (optional): hunger, health, happiness, cleanliness
    Positive hunger value means "reduces hunger by this amount".
    """
    if not shop_item.effect:
        return {}

    try:
        data = json.loads(shop_item.effect)
    except json.JSONDecodeError:
        # If effect data is invalid, treat as no effect
        return {}

    # Normalize to ints with defaults
    return {
        "hunger": int(data.get("hunger", 0)),
        "health": int(data.get("health", 0)),
        "happiness": int(data.get("happiness", 0)),
        "cleanliness": int(data.get("cleanliness", 0)),
    }


def apply_food_item_to_pet(pet: models.Pet, shop_item: models.ShopItem) -> Dict[str, Any]:
    """
    Apply a food item's effect to a pet.

    IMPORTANT SEMANTICS:
    - PET.hunger is a "how hungry" level (0–3).
      Higher = hungrier. Food REDUCES this value.
    - Effect 'hunger' is how many hunger points are satisfied (reduction amount).

    Returns a dict summarizing before/after values.
    """
    effects = parse_food_effect(shop_item)

    before = {
        "hunger": pet.hunger,
        "health": pet.health,
        "happiness": pet.happiness,
        "cleanliness": pet.cleanliness,
    }

    # Hunger: reduce by effect amount
    hunger_delta = effects.get("hunger", 0)
    if hunger_delta != 0:
        # Reduce hunger (cannot go below 0, cannot exceed 3)
        pet.hunger = clamp(pet.hunger - hunger_delta, 0, 3)

    # Health
    health_delta = effects.get("health", 0)
    if health_delta != 0:
        pet.health = clamp(pet.health + health_delta, 0, 100)

    # Happiness
    happiness_delta = effects.get("happiness", 0)
    if happiness_delta != 0:
        pet.happiness = clamp(pet.happiness + happiness_delta, 0, 100)

    # Cleanliness
    cleanliness_delta = effects.get("cleanliness", 0)
    if cleanliness_delta != 0:
        pet.cleanliness = clamp(pet.cleanliness + cleanliness_delta, 0, 100)

    pet.last_updated = datetime.datetime.utcnow()

    after = {
        "hunger": pet.hunger,
        "health": pet.health,
        "happiness": pet.happiness,
        "cleanliness": pet.cleanliness,
    }

    return {"before": before, "after": after, "effects": effects}


# Inventory / auto-feed helpers
def get_user_food_inventory(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Load all food items in a user's inventory.

    Returns a list of dicts:
    {
      "inventory": Inventory,
      "item": ShopItem,
      "effects": {...parsed effects...}
    }
    """
    rows = (
        db.query(models.Inventory, models.ShopItem)
        .join(models.ShopItem, models.Inventory.item_name == models.ShopItem.name)
        .filter(
            models.Inventory.user_id == user_id,
            models.Inventory.quantity > 0,
            models.ShopItem.category == "food",
        )
        .all()
    )

    result: List[Dict[str, Any]] = []
    for inv, shop_item in rows:
        result.append(
            {
                "inventory": inv,
                "item": shop_item,
                "effects": parse_food_effect(shop_item),
            }
        )
    return result


def pick_best_food_for_pet(
    pet: models.Pet, food_entries: List[Dict[str, Any]]
) -> Dict[str, Any] | None:
    """
    Pick the best food for a given pet.

    Strategy:
    - Only consider items that actually reduce hunger (effects["hunger"] > 0).
    - Choose the item with the largest hunger reduction and available quantity.

    Returns one entry from food_entries or None if nothing suitable.
    """
    best_entry = None
    best_hunger_reduction = 0

    for entry in food_entries:
        inv = entry["inventory"]
        effects = entry["effects"]

        if inv.quantity <= 0:
            continue

        hunger_reduction = effects.get("hunger", 0)
        if hunger_reduction > best_hunger_reduction:
            best_hunger_reduction = hunger_reduction
            best_entry = entry

    return best_entry


def check_can_feed_all(pets: List[models.Pet], food_entries: List[Dict[str, Any]]) -> bool:
    """
    Simulates feeding to see if there is enough food for ALL hungry pets.
    Does not modify database objects.
    """
    # Create a local map of inventory ID -> Quantity to simulate consumption
    sim_inventory = {
        entry["inventory"].id: entry["inventory"].quantity 
        for entry in food_entries
    }
    
    # We iterate a copy of hunger needs to avoid modifying the actual objects just in case
    for pet in pets:
        sim_hunger = pet.hunger
        
        while sim_hunger > 0:
            # Find best food in simulation inventory
            best_inv_id = None
            best_reduction = 0
            
            # Replicate pick_best_food logic but using sim_inventory map
            for entry in food_entries:
                inv_id = entry["inventory"].id
                qty = sim_inventory.get(inv_id, 0)
                
                if qty <= 0:
                    continue
                
                reduction = entry["effects"].get("hunger", 0)
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_inv_id = inv_id

            # If we couldn't find food for this pet, the check fails
            if best_inv_id is None:
                return False
            
            # "Consume" the food in simulation
            sim_inventory[best_inv_id] -= 1
            sim_hunger -= best_reduction
            # Note: sim_hunger can go negative (overfed), that's fine, loop breaks.

    return True


def auto_feed_user_pets(db: Session, owner_id: int) -> Dict[str, Any]:
    """
    Auto-feed all hungry guinea pigs for a given owner.

    Rules:
    - Only pets with species == 'guinea_pig' and hunger > 0 are considered.
    - NEW RULE: Only proceeds if there is enough food to feed EVERY hungry pet.
    - Pets are fed in order of highest hunger first.
    
    Returns a summary dict.
    """
    # Load hungry guinea pigs, highest hunger first
    pets = (
        db.query(models.Pet)
        .filter(
            models.Pet.owner_id == owner_id,
            models.Pet.species == "guinea_pig",
            models.Pet.hunger > 0,
        )
        .order_by(models.Pet.hunger.desc(), models.Pet.id.asc())
        .all()
    )

    if not pets:
        return {
            "owner_id": owner_id,
            "fed_pets": 0,
            "total_feedings": 0,
            "details": [],
            "success": True,
            "message": "No hungry pets."
        }

    food_entries = get_user_food_inventory(db, owner_id)
    if not food_entries:
        return {
            "owner_id": owner_id,
            "fed_pets": 0,
            "total_feedings": 0,
            "details": [],
            "success": False,
            "message": "No food in inventory."
        }

    # --- SIMULATION CHECK ---
    # Check if we have enough food for EVERYONE before feeding ANYONE
    if not check_can_feed_all(pets, food_entries):
        return {
            "owner_id": owner_id,
            "fed_pets": 0,
            "total_feedings": 0,
            "details": [],
            "success": False,
            "message": "Not enough food to feed all hungry pets."
        }

    # --- EXECUTION ---
    # If we get here, we know we have enough food. Proceed as normal.
    total_feedings = 0
    details: List[Dict[str, Any]] = []

    for pet in pets:
        pet_before_hunger = pet.hunger
        feedings_for_this_pet = 0

        # Keep feeding this pet until not hungry
        while pet.hunger > 0:
            entry = pick_best_food_for_pet(pet, food_entries)
            # entry should theoretically never be None here due to the check above,
            # but good to stay safe.
            if not entry:
                break 

            inv = entry["inventory"]
            shop_item = entry["item"]

            # Apply effect
            apply_food_item_to_pet(pet, shop_item)

            # Decrement inventory
            inv.quantity -= 1
            total_feedings += 1
            feedings_for_this_pet += 1

            if inv.quantity <= 0:
                # Remove exhausted item from list so it's not picked again
                food_entries = [
                    e for e in food_entries if e["inventory"].id != inv.id
                ]

            if not food_entries:
                break

            if pet.hunger <= 0:
                break

        if feedings_for_this_pet > 0 and pet.hunger < pet_before_hunger:
            details.append(
                {
                    "pet_id": pet.id,
                    "pet_name": pet.name,
                    "before_hunger": pet_before_hunger,
                    "after_hunger": pet.hunger,
                    "feedings_used": feedings_for_this_pet,
                }
            )

    # Remove any inventory entries with quantity <= 0 from DB
    for entry in food_entries:
        if entry["inventory"].quantity <= 0:
            db.delete(entry["inventory"])
    
    # Also check entries that were removed from the local list
    # Re-querying might be safer, but since we modify the objects in place,
    # SQLAlchemy tracking should handle the updates on commit. 
    # The explicit delete above handles the objects remaining in our local list.
    # To be thorough, we can trust SQLAlchemy to handle the updates to `quantity`.
    # But strictly deleting 0-qty rows is cleaner.

    # Log a single transaction summarizing auto-feed
    if total_feedings > 0:
        transaction = models.Transaction(
            user_id=owner_id,
            type="pet_auto_feed",
            amount=0,
            description=f"Auto-fed {len(details)} guinea pig(s) for {total_feedings} total feedings",
        )
        db.add(transaction)

    db.commit()

    return {
        "owner_id": owner_id,
        "fed_pets": len(details),
        "total_feedings": total_feedings,
        "details": details,
        "success": True,
        "message": "All pets fed successfully."
    }