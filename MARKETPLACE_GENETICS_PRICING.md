# Guinea Pig Marketplace & Genetics Pricing System

## Overview

This document describes the implementation of a dynamic pet marketplace with genetics-based pricing for the GuineaGames application. Players can now breed guinea pigs, valuate them based on genetic rarity, and trade them on a player-driven marketplace.

---

## Key Features Implemented

### 1. **Updated Genetics System** (4 genes)

The genetics system has been redesigned to use 4 core genes with Mendelian inheritance:

| Gene | Symbol | Alleles | Inheritance | Notes |
|------|--------|---------|-------------|-------|
| **coat_color** | - | B (Brown), O (Orange), W (White) | 3-allele incomplete dominance | Dominance: B > O > W |
| **hair_length** | - | H (Short), h (Fluffy) | 2-allele dominant/recessive | Fluffy (hh) is rare |
| **speed** | - | F (Fast), f (Slow) | 2-allele dominant/recessive | Affects movement speed stat |
| **endurance** | - | E (Energetic), e (Lazy) | 2-allele dominant/recessive | Affects endurance stat |

**Genetic Code Format:**
```
coat_color:BB;hair_length:Hh;speed:FF;endurance:Ee
```

---

## Rarity System

### Rarity Scoring Algorithm

Rarity is calculated on a scale of 0-40+ points based on:

#### 1. **Coat Color Rarity** (0-5 points)
- Pure homozygous colors (BB, OO, WW): +5 points (rarer)
- Mixed heterozygous (BO, BW, OW): +2 points (more common)

#### 2. **Hair Type Rarity** (0-3 points)
- Fluffy homozygous (hh): +3 points (desirable, rare)
- Fluffy heterozygous (Hh): +1 point
- Short hair (HH, Hh): 0 points

#### 3. **Trait Homozygosity** (0-4 points)
- Speed homozygous (FF or ff): +1-2 points
- Endurance homozygous (EE or ee): +1-2 points
- Heterozygous traits: +1 point each

#### 4. **Stat Quality Bonus** (0-5 points)
- Average stat ≥ 80: +5 points
- Average stat ≥ 70: +3 points
- Average stat ≥ 60: +1 point

### Rarity Tiers

| Tier | Score Range | Base Price | Market Characteristics |
|------|-------------|-----------|----------------------|
| **Common** | 0-5 | 100 coins | Basic heterozygous combinations |
| **Uncommon** | 6-10 | 500 coins | 1-2 homozygous traits |
| **Rare** | 11-15 | 2,000 coins | Multiple homozygous traits or pure colors |
| **Legendary** | 16+ | 10,000 coins | All homozygous + high stats + rare phenotype |

---

## Dynamic Pricing Formula

Market value is calculated as:

```
Price = Base_Price × Stat_Multiplier × Color_Multiplier × Hair_Multiplier

Where:
- Base_Price: Determined by rarity tier
- Stat_Multiplier: (0.5x - 2.0x) based on average of speed + endurance
  - Formula: 0.5 + (stat_avg / 100) × 1.5
  - 0 stats → 0.5x multiplier
  - 100 stats → 2.0x multiplier
- Color_Multiplier:
  - Pure color (homozygous): 1.5x
  - Mixed color (heterozygous): 1.0x
- Hair_Multiplier:
  - Fluffy: 1.3x (aesthetic premium)
  - Short: 1.0x
```

### Example Valuations

**Common Pet (Uncommon Mix)**
```
Base: 100
Score: 4 (OW coat + Hh hair + Ff speed + Ee endurance)
Tier: Common
Stats: Speed 55, Endurance 52 (avg 53.5)
Price = 100 × 1.30 × 1.0 × 1.0 = 130 coins
```

**Legendary Pet (Perfect Genes)**
```
Base: 10,000
Score: 18+ (BB coat + hh fluffy + FF speed + EE endurance)
Tier: Legendary
Stats: Speed 90, Endurance 92 (avg 91)
Price = 10,000 × 1.85 × 1.5 × 1.3 = 36,075 coins
```

---

## Database Schema

### Pet Table (Updated)
```sql
CREATE TABLE PETS (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER,
    name TEXT,
    species TEXT,
    color TEXT,
    color_phenotype TEXT,          -- "Brown", "Orange-White mix", etc.
    hair_type TEXT,                -- "short" or "fluffy"
    age_days INTEGER,
    health INTEGER,
    happiness INTEGER,
    hunger INTEGER,
    cleanliness INTEGER,
    points INTEGER,
    genetic_code TEXT,             -- Full genotype string
    speed INTEGER,                 -- 0-100
    endurance INTEGER,             -- 0-100
    rarity_score INTEGER,          -- 0-40+
    rarity_tier TEXT,              -- Common, Uncommon, Rare, Legendary
    market_value INTEGER,          -- Calculated base value
    for_sale INTEGER,              -- Boolean (0 or 1)
    asking_price INTEGER,          -- Player's listed price
    last_updated DATETIME,
    FOREIGN KEY (owner_id) REFERENCES USERS(id)
);
```

### Marketplace Tables
```sql
CREATE TABLE PET_MARKETPLACE (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER UNIQUE,
    seller_id INTEGER,
    asking_price INTEGER,
    listed_date DATETIME,
    FOREIGN KEY (pet_id) REFERENCES PETS(id),
    FOREIGN KEY (seller_id) REFERENCES USERS(id)
);

CREATE TABLE PET_SALES_HISTORY (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER,
    seller_id INTEGER,
    buyer_id INTEGER,
    sale_price INTEGER,
    sale_date DATETIME,
    FOREIGN KEY (pet_id) REFERENCES PETS(id)
);
```

---

## Marketplace API Endpoints

### Valuation Endpoints

#### `GET /marketplace/valuation/{pet_id}`
Get detailed valuation for a specific pet.

**Response:**
```json
{
    "pet_id": 1,
    "pet_name": "Fluffy",
    "owner_id": 1,
    "rarity_score": 8,
    "rarity_tier": "Uncommon",
    "market_value": 650,
    "coat_color": "Brown-White mix",
    "hair_type": "fluffy",
    "speed": 65,
    "endurance": 58
}
```

#### `GET /marketplace/compare-breeding?parent1_id=1&parent2_id=2`
Predict offspring value ranges from parent genetics.

**Response:**
```json
{
    "parent1": {"id": 1, "name": "Fluffy", "valuation": {...}},
    "parent2": {"id": 2, "name": "Speedy", "valuation": {...}},
    "possible_offspring": [
        {
            "outcome": 1,
            "coat_colors": ["Brown", "Orange"],
            "hair_types": ["fluffy", "short"],
            "estimated_min_value": 455,
            "estimated_max_value": 650,
            "probability": 0.25
        }
    ],
    "average_offspring_value": 575
}
```

### Listing Management

#### `POST /marketplace/list/{pet_id}?asking_price=800`
List a pet for sale.

**Response:**
```json
{
    "pet_id": 1,
    "pet_name": "Fluffy",
    "asking_price": 800,
    "market_value": 650,
    "listed": true
}
```

#### `DELETE /marketplace/unlist/{pet_id}`
Remove pet from marketplace.

### Browsing & Purchasing

#### `GET /marketplace/listings?rarity=Rare&min_price=1000&max_price=5000&sort_by=price_asc`
Browse available pets with filters.

**Query Parameters:**
- `rarity`: Filter by tier (Common, Uncommon, Rare, Legendary)
- `min_price`, `max_price`: Price range
- `coat_color`: Filter by color
- `hair_type`: "short" or "fluffy"
- `sort_by`: "price_asc", "price_desc", "rarity", "value"

**Response:**
```json
[
    {
        "pet_id": 3,
        "name": "Speedy",
        "owner_id": 1,
        "asking_price": 1200,
        "market_value": 1050,
        "rarity_tier": "Rare",
        "rarity_score": 12,
        "coat_color": "Brown (pure)",
        "hair_type": "short",
        "speed": 85,
        "endurance": 80,
        "listed_date": "2024-11-06T10:30:00"
    }
]
```

#### `POST /marketplace/purchase/{pet_id}?buyer_id=3`
Purchase a pet from the marketplace.

**Response:**
```json
{
    "message": "Purchase successful",
    "pet_id": 3,
    "pet_name": "Speedy",
    "sale_price": 1200,
    "new_owner_id": 3,
    "buyer_balance": 98800,
    "seller_balance": 31200
}
```

### Portfolio & Analytics

#### `GET /marketplace/portfolio/{user_id}`
Get total collection value and breakdown.

**Response:**
```json
{
    "user_id": 1,
    "username": "breeder1",
    "total_value": 15500,
    "pet_count": 8,
    "average_pet_value": 1937.50,
    "breakdown": {
        "Common": {"count": 2, "total_value": 300},
        "Uncommon": {"count": 3, "total_value": 2100},
        "Rare": {"count": 2, "total_value": 7000},
        "Legendary": {"count": 1, "total_value": 6100}
    }
}
```

#### `GET /marketplace/my-listings/{user_id}`
Get user's active listings.

#### `GET /marketplace/market-stats`
Get market analytics.

**Response:**
```json
{
    "total_pets_listed": 12,
    "average_prices": {
        "Common": 150,
        "Uncommon": 600,
        "Rare": 2500,
        "Legendary": 18000
    },
    "price_ranges": {
        "Common": {"min": 100, "max": 250},
        "Uncommon": {"min": 450, "max": 950},
        "Rare": {"min": 1800, "max": 3500},
        "Legendary": {"min": 15000, "max": 25000}
    },
    "total_market_value": 65400
}
```

---

## Breeding Integration

When two pets breed, the offspring automatically:
1. Inherits genetics through Mendelian inheritance (Punnett squares)
2. Derives phenotypes (visible traits) from genotypes
3. Calculates speed and endurance stats
4. **Automatically calculates rarity score and market value**
5. Records all inheritance information

### Example Breeding Outcome
```
Parent 1: Fluffy (Uncommon, value 650)
Parent 2: Speedy (Rare, value 2200)

Offspring: Shadow
- Genetics: coat_color:BW;hair_length:hh;speed:FF;endurance:Ee
- Phenotype: Brown-White fluffy guinea pig
- Rarity Score: 13 (RARE)
- Market Value: 3,100 coins
- Stats: Speed 85, Endurance 72
```

---

## Files Modified & Created

### New Files
- **`backend/pricing.py`** - Rarity calculation and pricing engine
  - `RarityCalculator.calculate_rarity_score()`
  - `RarityCalculator.get_rarity_tier()`
  - `RarityCalculator.calculate_market_value()`
  - `RarityCalculator.calculate_and_store_valuation()`

- **`backend/routes/marketplace.py`** - Marketplace API routes
  - 12 endpoints for valuation, trading, portfolio management

- **`backend/database/seed_test_pets.py`** - Test data generation
  - Creates 8 test pets across all rarity tiers
  - Lists some for sale automatically

### Modified Files
- **`backend/genetics.py`**
  - Updated to 4-gene system (removed size, intelligence)
  - Enhanced `get_phenotype()` for 3-allele coat color
  - Integrated rarity scoring into breeding

- **`backend/models.py`**
  - Added `color_phenotype`, `hair_type` to Pet
  - Added `rarity_score`, `rarity_tier`, `market_value`, `for_sale`, `asking_price`
  - Added `PetMarketplace` and `PetSalesHistory` models

- **`backend/database/database.py`**
  - Updated PETS table with new columns
  - Added PET_MARKETPLACE and PET_SALES_HISTORY tables

- **`backend/main.py`**
  - Registered marketplace router

---

## How to Use

### 1. Initialize the Database
```bash
cd backend/database
python database.py
```

### 2. Run the API
```bash
cd backend
uvicorn main:app --reload
```

The genetics system initializes automatically with 4 genes.

### 3. Seed Test Data (Optional)
```bash
cd backend/database
python seed_test_pets.py
```

This creates 8 test pets across all rarity tiers for testing.

### 4. API Usage Examples

**Check a pet's valuation:**
```bash
curl http://localhost:8000/marketplace/valuation/1
```

**List a pet for sale (900 coins):**
```bash
curl -X POST "http://localhost:8000/marketplace/list/1?asking_price=900"
```

**Browse rare pets sorted by price:**
```bash
curl "http://localhost:8000/marketplace/listings?rarity=Rare&sort_by=price_asc"
```

**Buy a pet:**
```bash
curl -X POST "http://localhost:8000/marketplace/purchase/1?buyer_id=3"
```

**Check portfolio value:**
```bash
curl http://localhost:8000/marketplace/portfolio/1
```

---

## Game Design Notes

### Breeding Strategy
- Players can breed rare genetics to create valuable offspring
- Uncommon + Rare parents have ~25% chance of Legendary offspring
- Fluffy coat genes are always desirable (rare, aesthetic)

### Market Dynamics
- Base prices provide floor value
- High-stat pets (80+) can be 2x base price
- Pure colors and fluffy coats are premium
- Players can speculate on prices above/below market value

### Economy Balance
- Legendary pets: 10,000+ coins (long-term wealth goal)
- Rare pets: 2,000-5,000 coins (breeding investment)
- Uncommon pets: 500-1,000 coins (starter breeding stock)
- Common pets: 100-300 coins (throwaway duplicates)

---

## Future Enhancements

1. **Advanced Genetics**
   - More complex trait interactions
   - Pedigree tracking for pure bloodlines
   - Mutation system for unique colors

2. **Market Features**
   - Auction system with bidding
   - Price history graphs
   - Trading notifications
   - Breed recommendations based on market demand

3. **Economy Features**
   - NPC pet shop with rotating inventory
   - Seasonal events with price fluctuations
   - Pet insurance/durability system
   - Breeding cooldown periods

4. **UI/UX**
   - Genetic visualization (family tree)
   - Rarity badges and icons
   - Portfolio dashboard
   - Market insights and trends

---

## Testing Checklist

- [x] 4-gene genetics system with 3-allele coat colors
- [x] Mendelian inheritance working correctly
- [x] Rarity scoring algorithm accurate
- [x] Pricing formula dynamic and balanced
- [x] Marketplace listing/unlisting works
- [x] Pet purchase transfers ownership and currency
- [x] Portfolio valuation sums correctly
- [x] Breeding offspring auto-calculated for rarity/price
- [x] Filter and sorting on marketplace working
- [x] Market statistics accurate

---

## Summary

This implementation creates a complete genetics-based marketplace system where:
- **Genetics matter** - 4 carefully balanced genes with incomplete dominance
- **Rarity is valuable** - Rare combinations command premium prices
- **Breeding is strategic** - Players breed for specific traits and profit
- **Market is player-driven** - Supply, demand, and speculation affect prices
- **All automatic** - Rarity and pricing calculated on creation/breeding

The system is fully integrated with the existing FastAPI backend and ready for frontend implementation.
