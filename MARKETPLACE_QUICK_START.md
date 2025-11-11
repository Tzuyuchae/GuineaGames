# Marketplace & Pricing Quick Start Guide

## What Was Implemented

A complete **genetics-based pricing and marketplace system** for Guinea Games where:
- Pet values are determined by their genetics (coat color, hair type, speed, endurance)
- Rare genetics = higher prices
- Players can list, browse, and trade pets on a dynamic marketplace
- All valuation is automatic based on genetic rarity

---

## Key Components

### 1. **Genetics System** (4 Genes)
```
coat_color (3 alleles: B/O/W) → visible color phenotype
hair_length (2 alleles: H/h) → short or fluffy
speed (2 alleles: F/f) → movement speed stat
endurance (2 alleles: E/e) → stamina stat
```

### 2. **Rarity Tiers**
- **Common** (0-5 pts): Basic mix → 100 coins base
- **Uncommon** (6-10 pts): 1-2 homozygous traits → 500 coins base
- **Rare** (11-15 pts): Multiple homozygous traits → 2,000 coins base
- **Legendary** (16+ pts): All homozygous + high stats → 10,000 coins base

### 3. **Dynamic Pricing**
```
Price = Base × (Stat Multiplier) × (Color Multiplier) × (Hair Multiplier)

Example: Legendary with 90 avg stats, pure brown, fluffy
= 10,000 × 1.85 × 1.5 × 1.3 = 36,075 coins
```

### 4. **Marketplace Features**
- List pets for sale (set your own price)
- Browse with filters (rarity, price, hair type, etc.)
- Purchase pets (transfers ownership + currency)
- View portfolio value
- Compare breeding potential

---

## Getting Started

### Step 1: Initialize Database
```bash
cd backend/database
python database.py
```

### Step 2: Start the API
```bash
cd backend
uvicorn main:app --reload
```

### Step 3: (Optional) Seed Test Data
```bash
cd backend/database
python seed_test_pets.py
```

Creates 8 test pets across all rarity tiers for testing.

---

## API Endpoints (12 Total)

### Valuation
- `GET /marketplace/valuation/{pet_id}` - Get pet value & rarity
- `GET /marketplace/compare-breeding?parent1_id=1&parent2_id=2` - Predict offspring value

### Listing
- `POST /marketplace/list/{pet_id}?asking_price=800` - List pet for sale
- `DELETE /marketplace/unlist/{pet_id}` - Remove from sale

### Trading
- `GET /marketplace/listings` - Browse pets (with filters & sorting)
- `POST /marketplace/purchase/{pet_id}?buyer_id=3` - Buy a pet

### Portfolio
- `GET /marketplace/portfolio/{user_id}` - Total collection value
- `GET /marketplace/my-listings/{user_id}` - Your listings
- `GET /marketplace/market-stats` - Market analytics

---

## Example Workflow

### 1. Get Pet Valuation
```bash
curl http://localhost:8000/marketplace/valuation/1
```
Response:
```json
{
  "pet_id": 1,
  "rarity_tier": "Rare",
  "rarity_score": 12,
  "market_value": 2450,
  "coat_color": "Brown (pure)",
  "hair_type": "fluffy",
  "speed": 82,
  "endurance": 78
}
```

### 2. List for Sale
```bash
curl -X POST "http://localhost:8000/marketplace/list/1?asking_price=2500"
```

### 3. Browse Rare Pets
```bash
curl "http://localhost:8000/marketplace/listings?rarity=Rare&sort_by=price_asc"
```

### 4. Buy a Pet
```bash
curl -X POST "http://localhost:8000/marketplace/purchase/3?buyer_id=5"
```

### 5. Check Your Portfolio
```bash
curl http://localhost:8000/marketplace/portfolio/5
```
Response:
```json
{
  "user_id": 5,
  "username": "collector",
  "total_value": 45250,
  "pet_count": 15,
  "breakdown": {
    "Common": {"count": 3, "total_value": 400},
    "Uncommon": {"count": 5, "total_value": 3200},
    "Rare": {"count": 6, "total_value": 18000},
    "Legendary": {"count": 1, "total_value": 23650}
  }
}
```

---

## Rarity Scoring Examples

### Common Pet (Heterozygous Mix)
```
Genetics: OW coat, Hh hair, Ff speed, Ee endurance
Score: 4 points
Stats: 50 speed, 50 endurance
Price: 100 × 1.0 × 1.0 × 1.0 = 100 coins
```

### Uncommon Pet (Some Homozygous)
```
Genetics: BB coat, Hh hair, FF speed, Ee endurance
Score: 7 points
Stats: 75 speed, 60 endurance
Price: 500 × 1.35 × 1.5 × 1.0 = 1,012 coins
```

### Rare Pet (Multiple Homozygous)
```
Genetics: WW coat, hh hair, FF speed, EE endurance
Score: 13 points
Stats: 85 speed, 82 endurance
Price: 2,000 × 1.68 × 1.0 × 1.3 = 4,368 coins
```

### Legendary Pet (Perfect Genes)
```
Genetics: BB coat, hh hair, FF speed, EE endurance
Score: 18+ points
Stats: 92 speed, 90 endurance
Price: 10,000 × 1.82 × 1.5 × 1.3 = 35,430 coins
```

---

## Breeding → Valuation Flow

1. **Breed two pets** → Offspring created with inherited genetics
2. **Stats calculated** → Speed & endurance from genetic effects
3. **Rarity scored** → Automatic calculation of rarity points
4. **Price set** → Market value calculated based on rarity + stats
5. **Phenotype stored** → Color description saved (e.g., "Brown-Orange mix")

All automatic! No manual intervention needed.

---

## Database Tables

**Modified:**
- `PETS` - Added: `color_phenotype`, `hair_type`, `rarity_score`, `rarity_tier`, `market_value`, `for_sale`, `asking_price`

**New:**
- `PET_MARKETPLACE` - Active listings with asking prices
- `PET_SALES_HISTORY` - Completed transactions

---

## Files Created/Modified

### New Files
- `backend/pricing.py` - Rarity calculation engine
- `backend/routes/marketplace.py` - 12 API endpoints
- `backend/database/seed_test_pets.py` - Test data generator
- `MARKETPLACE_GENETICS_PRICING.md` - Full documentation
- `MARKETPLACE_QUICK_START.md` - This file

### Modified Files
- `backend/genetics.py` - 4-gene system, auto pricing on breed
- `backend/models.py` - Pet model extended with marketplace fields
- `backend/database/database.py` - Schema updated with new columns & tables
- `backend/main.py` - Marketplace router registered

---

## Next Steps for Frontend

### Display Pet Value
```python
# Show rarity badge and market value
pet_value = GET /marketplace/valuation/{pet_id}
display_rarity_badge(pet_value['rarity_tier'])
display_price(pet_value['market_value'])
```

### Marketplace UI
```python
# Browse listings
GET /marketplace/listings?rarity=Rare&sort_by=price_asc

# Show filters:
# - Rarity tier selector
# - Price range slider
# - Hair type toggle (short/fluffy)
# - Coat color filter
```

### Purchase Flow
```python
# 1. Show pet details + price
# 2. Check buyer balance
# 3. Confirm purchase
# 4. POST /marketplace/purchase/{pet_id}?buyer_id={user_id}
# 5. Update inventory + balance
```

### Portfolio Dashboard
```python
# GET /marketplace/portfolio/{user_id}
# Show:
# - Total collection value
# - Breakdown by rarity tier
# - List of owned pets with values
```

---

## Testing

Run the seed script to generate test data:
```bash
python backend/database/seed_test_pets.py
```

This creates:
- 3 test users (breeder1, breeder2, collector)
- 8 test pets (Common → Legendary)
- 4 listed for sale

Then test all endpoints:
```bash
# Get valuations
curl http://localhost:8000/marketplace/valuation/1

# Browse listings
curl http://localhost:8000/marketplace/listings

# Check portfolio
curl http://localhost:8000/marketplace/portfolio/1

# Get market stats
curl http://localhost:8000/marketplace/market-stats
```

---

## Summary

✅ **Complete implementation of:**
- Genetics-based rarity system (4 genes, 27 color possibilities)
- Dynamic pricing formula (base × multipliers)
- Full marketplace API (12 endpoints)
- Automatic valuation on breeding
- Player portfolio tracking
- Market analytics

Ready for frontend integration! 🚀
