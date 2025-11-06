"""
Marketplace API Routes
Handles pet trading, valuation, and portfolio management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from pricing import RarityCalculator

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


# =====================
# VALUATION ENDPOINTS
# =====================

@router.get("/valuation/{pet_id}", response_model=dict)
def get_pet_valuation(pet_id: int, db: Session = Depends(get_db)):
    """
    Get detailed valuation for a pet.
    Returns rarity score, tier, market value, and phenotype info.
    """
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Calculate if not already done
    if pet.rarity_score == 0 or not pet.market_value:
        valuation = RarityCalculator.calculate_and_store_valuation(pet, db)
        db.commit()
    else:
        valuation = {
            "rarity_score": pet.rarity_score,
            "rarity_tier": pet.rarity_tier,
            "market_value": pet.market_value,
            "coat_color": pet.color_phenotype,
            "hair_type": pet.hair_type,
            "speed": pet.speed,
            "endurance": pet.endurance
        }

    # Add ownership info
    valuation["pet_id"] = pet_id
    valuation["pet_name"] = pet.name
    valuation["owner_id"] = pet.owner_id

    return valuation


@router.get("/compare-breeding")
def compare_breeding_value(parent1_id: int, parent2_id: int, db: Session = Depends(get_db)):
    """
    Analyze breeding potential and predict offspring value ranges.
    Shows all 4 possible offspring outcomes with estimated values.
    """
    parent1 = db.query(models.Pet).filter(models.Pet.id == parent1_id).first()
    parent2 = db.query(models.Pet).filter(models.Pet.id == parent2_id).first()

    if not parent1 or not parent2:
        raise HTTPException(status_code=404, detail="One or both parents not found")

    # Get parent valuations
    p1_val = RarityCalculator.calculate_and_store_valuation(parent1, db)
    p2_val = RarityCalculator.calculate_and_store_valuation(parent2, db)

    # Simulate 4 possible offspring based on Mendelian inheritance
    # For coat_color, hair_length, speed, endurance genes
    offspring_outcomes = []

    for i in range(4):  # 4 possible combinations from Punnett squares
        # Simplified: show possible phenotypes
        outcome = {
            "outcome": i + 1,
            "coat_colors": _get_possible_coat_colors(parent1.genetic_code, parent2.genetic_code),
            "hair_types": _get_possible_hair_types(parent1.genetic_code, parent2.genetic_code),
            "estimated_min_value": int(parent1.market_value * 0.7),  # Conservative estimate
            "estimated_max_value": int(max(parent1.market_value, parent2.market_value) * 1.2),
            "probability": 0.25  # Equal probability for each outcome
        }
        offspring_outcomes.append(outcome)

    return {
        "parent1": {"id": parent1_id, "name": parent1.name, "valuation": p1_val},
        "parent2": {"id": parent2_id, "name": parent2.name, "valuation": p2_val},
        "possible_offspring": offspring_outcomes,
        "average_offspring_value": int(sum(o["estimated_max_value"] for o in offspring_outcomes) / len(offspring_outcomes))
    }


# =====================
# LISTING MANAGEMENT
# =====================

@router.post("/list/{pet_id}")
def list_pet_for_sale(pet_id: int, asking_price: int, db: Session = Depends(get_db)):
    """
    List a pet for sale on the marketplace.
    Owner sets the asking price.
    """
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    if asking_price <= 0:
        raise HTTPException(status_code=400, detail="Asking price must be greater than 0")

    # Check if already listed
    existing_listing = db.query(models.PetMarketplace).filter(
        models.PetMarketplace.pet_id == pet_id
    ).first()

    if existing_listing:
        # Update existing listing
        existing_listing.asking_price = asking_price
    else:
        # Create new listing
        listing = models.PetMarketplace(
            pet_id=pet_id,
            seller_id=pet.owner_id,
            asking_price=asking_price
        )
        db.add(listing)

    # Update pet status
    pet.for_sale = 1
    pet.asking_price = asking_price

    db.commit()

    # Get updated valuation
    valuation = {
        "pet_id": pet_id,
        "pet_name": pet.name,
        "asking_price": asking_price,
        "market_value": pet.market_value,
        "listed": True
    }

    return valuation


@router.delete("/unlist/{pet_id}")
def unlist_pet_from_sale(pet_id: int, db: Session = Depends(get_db)):
    """Remove a pet from the marketplace"""
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Remove marketplace listing
    listing = db.query(models.PetMarketplace).filter(
        models.PetMarketplace.pet_id == pet_id
    ).first()

    if listing:
        db.delete(listing)

    # Update pet status
    pet.for_sale = 0
    pet.asking_price = None

    db.commit()

    return {"message": f"Pet {pet.name} unlisted from marketplace"}


# =====================
# BROWSING & PURCHASING
# =====================

@router.get("/listings")
def get_marketplace_listings(
    rarity: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    coat_color: str = Query(None),
    hair_type: str = Query(None),
    sort_by: str = Query("price_asc"),
    db: Session = Depends(get_db)
):
    """
    Browse available pets for sale.

    Query parameters:
    - rarity: "Common", "Uncommon", "Rare", "Legendary"
    - min_price, max_price: Price range
    - coat_color: Filter by color (Brown, Orange, White, mix)
    - hair_type: "short" or "fluffy"
    - sort_by: "price_asc", "price_desc", "rarity", "value"
    """
    query = db.query(models.Pet, models.PetMarketplace).join(
        models.PetMarketplace,
        models.Pet.id == models.PetMarketplace.pet_id
    )

    # Apply filters
    if rarity:
        query = query.filter(models.Pet.rarity_tier == rarity)

    if min_price is not None:
        query = query.filter(models.PetMarketplace.asking_price >= min_price)

    if max_price is not None:
        query = query.filter(models.PetMarketplace.asking_price <= max_price)

    if hair_type:
        query = query.filter(models.Pet.hair_type == hair_type)

    if coat_color:
        # Search in color_phenotype field
        query = query.filter(models.Pet.color_phenotype.contains(coat_color))

    # Apply sorting
    if sort_by == "price_desc":
        query = query.order_by(models.PetMarketplace.asking_price.desc())
    elif sort_by == "rarity":
        # Order: Legendary > Rare > Uncommon > Common
        tier_order = {"Legendary": 4, "Rare": 3, "Uncommon": 2, "Common": 1}
        query = query.order_by(models.Pet.rarity_score.desc())
    elif sort_by == "value":
        query = query.order_by(models.Pet.market_value.desc())
    else:  # price_asc (default)
        query = query.order_by(models.PetMarketplace.asking_price.asc())

    listings = query.all()

    # Format response
    result = []
    for pet, listing in listings:
        result.append({
            "pet_id": pet.id,
            "name": pet.name,
            "owner_id": pet.owner_id,
            "asking_price": listing.asking_price,
            "market_value": pet.market_value,
            "rarity_tier": pet.rarity_tier,
            "rarity_score": pet.rarity_score,
            "coat_color": pet.color_phenotype,
            "hair_type": pet.hair_type,
            "speed": pet.speed,
            "endurance": pet.endurance,
            "listed_date": listing.listed_date
        })

    return result


@router.post("/purchase/{pet_id}")
def purchase_pet(pet_id: int, buyer_id: int, db: Session = Depends(get_db)):
    """
    Purchase a pet from the marketplace.
    Transfers ownership, updates balance, and logs transaction.
    """
    # Get pet and listing
    pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    listing = db.query(models.PetMarketplace).filter(
        models.PetMarketplace.pet_id == pet_id
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Pet not listed for sale")

    # Get buyer and seller
    buyer = db.query(models.User).filter(models.User.id == buyer_id).first()
    seller = db.query(models.User).filter(models.User.id == listing.seller_id).first()

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    # Check funds
    if buyer.balance < listing.asking_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Prevent buying own pet
    if buyer_id == listing.seller_id:
        raise HTTPException(status_code=400, detail="Cannot buy your own pet")

    # Execute transaction
    sale_price = listing.asking_price

    # Update balances
    buyer.balance -= sale_price
    seller.balance += sale_price

    # Transfer ownership
    pet.owner_id = buyer_id

    # Log transactions for both parties
    buyer_transaction = models.Transaction(
        user_id=buyer_id,
        type="pet_purchase",
        amount=-sale_price,
        description=f"Purchased {pet.name} from user {seller.username}"
    )
    seller_transaction = models.Transaction(
        user_id=listing.seller_id,
        type="pet_sale",
        amount=sale_price,
        description=f"Sold {pet.name} to user {buyer.username}"
    )

    # Log sales history
    sales_record = models.PetSalesHistory(
        pet_id=pet_id,
        seller_id=listing.seller_id,
        buyer_id=buyer_id,
        sale_price=sale_price
    )

    # Remove from marketplace
    db.delete(listing)
    pet.for_sale = 0
    pet.asking_price = None

    # Commit all changes
    db.add(buyer_transaction)
    db.add(seller_transaction)
    db.add(sales_record)
    db.commit()

    return {
        "message": "Purchase successful",
        "pet_id": pet_id,
        "pet_name": pet.name,
        "sale_price": sale_price,
        "new_owner_id": buyer_id,
        "buyer_balance": buyer.balance,
        "seller_balance": seller.balance
    }


# =====================
# PORTFOLIO & ANALYTICS
# =====================

@router.get("/portfolio/{user_id}")
def get_user_portfolio(user_id: int, db: Session = Depends(get_db)):
    """
    Get total collection value and portfolio breakdown for a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pets = db.query(models.Pet).filter(models.Pet.owner_id == user_id).all()

    if not pets:
        return {
            "user_id": user_id,
            "username": user.username,
            "total_value": 0,
            "pet_count": 0,
            "breakdown": {}
        }

    # Recalculate valuations if needed
    for pet in pets:
        if pet.rarity_score == 0 or pet.market_value == 0:
            RarityCalculator.calculate_and_store_valuation(pet, db)

    # Sum up values by tier
    breakdown = {
        "Common": {"count": 0, "total_value": 0},
        "Uncommon": {"count": 0, "total_value": 0},
        "Rare": {"count": 0, "total_value": 0},
        "Legendary": {"count": 0, "total_value": 0}
    }

    total_value = 0
    for pet in pets:
        tier = pet.rarity_tier or "Common"
        breakdown[tier]["count"] += 1
        breakdown[tier]["total_value"] += pet.market_value
        total_value += pet.market_value

    db.commit()

    return {
        "user_id": user_id,
        "username": user.username,
        "total_value": total_value,
        "pet_count": len(pets),
        "breakdown": breakdown,
        "average_pet_value": int(total_value / len(pets)) if pets else 0
    }


@router.get("/my-listings/{user_id}")
def get_user_listings(user_id: int, db: Session = Depends(get_db)):
    """Get all active listings for a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    listings = db.query(models.Pet, models.PetMarketplace).join(
        models.PetMarketplace,
        models.Pet.id == models.PetMarketplace.pet_id
    ).filter(models.PetMarketplace.seller_id == user_id).all()

    result = []
    for pet, listing in listings:
        result.append({
            "pet_id": pet.id,
            "name": pet.name,
            "asking_price": listing.asking_price,
            "market_value": pet.market_value,
            "rarity_tier": pet.rarity_tier,
            "coat_color": pet.color_phenotype,
            "hair_type": pet.hair_type,
            "listed_date": listing.listed_date
        })

    return result


@router.get("/market-stats")
def get_market_statistics(db: Session = Depends(get_db)):
    """Get market analytics and statistics"""
    # Get all listings
    listings = db.query(models.Pet, models.PetMarketplace).join(
        models.PetMarketplace,
        models.Pet.id == models.PetMarketplace.pet_id
    ).all()

    if not listings:
        return {
            "total_pets_listed": 0,
            "average_prices": {},
            "price_range": {}
        }

    # Calculate stats by tier
    stats_by_tier = {
        "Common": {"count": 0, "total_price": 0, "prices": []},
        "Uncommon": {"count": 0, "total_price": 0, "prices": []},
        "Rare": {"count": 0, "total_price": 0, "prices": []},
        "Legendary": {"count": 0, "total_price": 0, "prices": []}
    }

    for pet, listing in listings:
        tier = pet.rarity_tier or "Common"
        stats_by_tier[tier]["count"] += 1
        stats_by_tier[tier]["total_price"] += listing.asking_price
        stats_by_tier[tier]["prices"].append(listing.asking_price)

    # Calculate averages and ranges
    average_prices = {}
    price_ranges = {}

    for tier, stats in stats_by_tier.items():
        if stats["count"] > 0:
            avg = int(stats["total_price"] / stats["count"])
            average_prices[tier] = avg
            price_ranges[tier] = {
                "min": min(stats["prices"]),
                "max": max(stats["prices"])
            }

    return {
        "total_pets_listed": len(listings),
        "average_prices": average_prices,
        "price_ranges": price_ranges,
        "total_market_value": sum(listing.asking_price for _, listing in listings)
    }


# =====================
# HELPER FUNCTIONS
# =====================

def _get_possible_coat_colors(genetic_code1: str, genetic_code2: str) -> list:
    """Get possible coat colors from parent genetics"""
    genes1 = RarityCalculator.parse_genetic_code(genetic_code1)
    genes2 = RarityCalculator.parse_genetic_code(genetic_code2)

    coat1 = genes1.get("coat_color", "WW")
    coat2 = genes2.get("coat_color", "WW")

    # Simplified: show parent genotypes
    colors = {
        "B": "Brown",
        "O": "Orange",
        "W": "White"
    }

    possible = set()
    for a1 in coat1:
        for a2 in coat2:
            possible.add(colors.get(a1, "Unknown"))
            possible.add(colors.get(a2, "Unknown"))

    return list(possible)


def _get_possible_hair_types(genetic_code1: str, genetic_code2: str) -> list:
    """Get possible hair types from parent genetics"""
    genes1 = RarityCalculator.parse_genetic_code(genetic_code1)
    genes2 = RarityCalculator.parse_genetic_code(genetic_code2)

    hair1 = genes1.get("hair_length", "HH")
    hair2 = genes2.get("hair_length", "HH")

    possible = set()

    # If either parent can pass 'h', fluffy is possible
    if "h" in hair1 or "h" in hair2:
        possible.add("fluffy")

    # Short is likely possible
    if "H" in hair1 or "H" in hair2:
        possible.add("short")

    return list(possible) if possible else ["short"]
