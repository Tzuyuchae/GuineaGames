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


def auto_feed_user_pets(db: Session, owner_id: int) -> Dict[str, Any]:
    """
    Auto-feed all hungry guinea pigs for a given owner.

    Rules:
    - Only pets with species == 'guinea_pig' and hunger > 0 are considered.
    - Pets are fed in order of highest hunger first.
    - Uses items from the owner's inventory where category == 'food' and
      effect.hunger > 0.
    - Stops when all guinea pigs are no longer hungry OR food runs out.

    Returns a summary dict:
    {
      "owner_id": ...,
      "fed_pets": <number of pets whose hunger decreased>,
      "total_feedings": <number of individual feed actions>,
      "details": [
         {
           "pet_id": ...,
           "pet_name": ...,
           "before_hunger": ...,
           "after_hunger": ...,
           "feedings_used": ...
         },
         ...
      ]
    }
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
        }

    food_entries = get_user_food_inventory(db, owner_id)
    if not food_entries:
        return {
            "owner_id": owner_id,
            "fed_pets": 0,
            "total_feedings": 0,
            "details": [],
        }

    total_feedings = 0
    details: List[Dict[str, Any]] = []

    for pet in pets:
        pet_before_hunger = pet.hunger
        feedings_for_this_pet = 0

        # Keep feeding this pet until not hungry or out of suitable food
        while pet.hunger > 0:
            entry = pick_best_food_for_pet(pet, food_entries)
            if not entry:
                break  # No more usable food

            inv = entry["inventory"]
            shop_item = entry["item"]

            # Apply effect
            apply_food_item_to_pet(pet, shop_item)

            # Decrement inventory
            inv.quantity -= 1
            total_feedings += 1
            feedings_for_this_pet += 1

            if inv.quantity <= 0:
                # Remove exhausted item from list
                food_entries = [
                    e for e in food_entries if e["inventory"].id != inv.id
                ]

            # If there is no food left at all, break outer loop after this pet
            if not food_entries:
                break

            # If pet is now full (hunger == 0), move on
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

        # If absolutely no food left, we stop processing more pets
        if not food_entries:
            break

    # Remove any inventory entries with quantity <= 0 from DB
    for entry in food_entries:
        if entry["inventory"].quantity <= 0:
            db.delete(entry["inventory"])

    # Log a single transaction summarizing auto-feed (optional, amount 0)
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
    }
