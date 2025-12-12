from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

# --- GENERIC SCHEMAS ---

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    balance: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class InventoryBase(BaseModel):
    item_name: str
    quantity: int

class InventoryCreate(InventoryBase):
    user_id: int

class InventoryUpdate(BaseModel):
    quantity: int

class Inventory(InventoryBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# --- PET SCHEMAS ---

class PetBase(BaseModel):
    name: str
    species: str
    color: str

class PetCreate(PetBase):
    owner_id: int
    coat_length: Optional[str] = "Short"
    speed: Optional[int] = None
    endurance: Optional[int] = None
    market_value: Optional[int] = None

class PetUpdate(BaseModel):
    name: Optional[str] = None
    age_days: Optional[int] = None
    health: Optional[int] = None
    happiness: Optional[int] = None
    hunger: Optional[int] = None
    cleanliness: Optional[int] = None

class Pet(PetBase):
    id: int
    owner_id: int
    age_days: int
    age_months: int
    health: int
    happiness: int
    hunger: int
    cleanliness: int
    
    # Stats
    speed: int
    endurance: int
    rarity_score: int
    rarity_tier: str
    market_value: int
    
    # Visuals
    color_phenotype: Optional[str]
    hair_type: Optional[str]
    
    genetic_code: Optional[str]
    
    # --- NEW FIELD ADDED HERE ---
    breeding_cooldown: int = 0
    
    class Config:
        from_attributes = True

# --- OTHER SCHEMAS ---

class TransactionCreate(BaseModel):
    user_id: int
    type: str
    amount: int
    description: str

class Transaction(TransactionCreate):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MiniGameBase(BaseModel):
    name: str
    base_reward: int
    cooldown_sec: int

class MiniGameCreate(MiniGameBase):
    pass

class MiniGame(MiniGameBase):
    id: int
    
    class Config:
        from_attributes = True

class LeaderboardCreate(BaseModel):
    user_id: int
    score: int

class Leaderboard(LeaderboardCreate):
    id: int
    rank: Optional[int]
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- GENETICS SCHEMAS ---

class GeneCreate(BaseModel):
    name: str
    trait: str
    description: Optional[str] = None

class Gene(GeneCreate):
    id: int
    class Config:
        from_attributes = True

class AlleleCreate(BaseModel):
    gene_id: int
    name: str
    symbol: str
    dominance_level: int
    effect_value: int
    description: Optional[str] = None

class Allele(AlleleCreate):
    id: int
    class Config:
        from_attributes = True

class PetGeneticsCreate(BaseModel):
    pet_id: int
    gene_id: int
    allele1_id: int
    allele2_id: int

class PetGenetics(PetGeneticsCreate):
    id: int
    class Config:
        from_attributes = True

class BreedingRequest(BaseModel):
    parent1_id: int
    parent2_id: int
    child_name: str
    child_species: Optional[str] = "Guinea Pig"
    child_color: Optional[str] = "Mixed"
    owner_id: int

class PunnettSquareResult(BaseModel):
    gene_name: str
    parent1_genotype: str
    parent2_genotype: str
    possible_offspring: List[str]
    probabilities: Dict[str, float]
    punnett_square: List[List[str]]

class BreedingOutcome(BaseModel):
    child_id: int
    child_name: str
    child_genetics: str
    punnett_squares: List[PunnettSquareResult]
    estimated_stats: Dict[str, int]
    inheritance_summary: List[str]

class PetStatsSchema(BaseModel):
    speed: int
    endurance: int
    genetic_score: int
    
class FeedPetRequest(BaseModel):
    item_name: str