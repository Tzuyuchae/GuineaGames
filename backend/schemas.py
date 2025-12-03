from pydantic import BaseModel
from typing import Optional, List
import datetime

# =====================
# USER SCHEMAS
# =====================
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    balance: int = 0
    pets: List['Pet'] = []

    class Config:
        from_attributes = True

# =====================
# PET SCHEMAS
# =====================
class PetBase(BaseModel):
    name: str
    species: str
    color: str

class PetCreate(PetBase):
    owner_id: int

class Pet(PetBase):
    id: int
    owner_id: int
    age_days: int
    health: int
    happiness: int
    hunger: int
    cleanliness: int
    points: int
    genetic_code: Optional[str] = None
    speed: int
    endurance: int
    last_updated: datetime.datetime

    class Config:
        from_attributes = True

class PetUpdate(BaseModel):
    name: Optional[str] = None
    health: Optional[int] = None
    happiness: Optional[int] = None
    hunger: Optional[int] = None
    cleanliness: Optional[int] = None
    age_days: Optional[int] = None

# =====================
# INVENTORY SCHEMAS
# =====================
class InventoryBase(BaseModel):
    item_name: str
    quantity: int

class InventoryCreate(InventoryBase):
    user_id: int

class Inventory(InventoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class InventoryUpdate(BaseModel):
    quantity: int

# =====================
# TRANSACTION SCHEMAS
# =====================
class TransactionBase(BaseModel):
    type: str
    amount: int
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: int

class Transaction(TransactionBase):
    id: int
    user_id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

# =====================
# MINI_GAME SCHEMAS
# =====================
class MiniGameBase(BaseModel):
    name: str
    base_reward: int
    cooldown_sec: Optional[int] = None

class MiniGameCreate(MiniGameBase):
    pass

class MiniGame(MiniGameBase):
    id: int

    class Config:
        from_attributes = True

# =====================
# LEADERBOARD SCHEMAS
# =====================
class LeaderboardBase(BaseModel):
    score: int

class LeaderboardCreate(LeaderboardBase):
    user_id: int

class Leaderboard(LeaderboardBase):
    id: int
    user_id: int
    rank: Optional[int] = None
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# =====================
# SHOP_ITEM SCHEMAS
# =====================
class ShopItemBase(BaseModel):
    name: str
    category: str = 'food'
    cost: int
    description: Optional[str] = None
    effect: Optional[str] = None

class ShopItemCreate(ShopItemBase):
    pass

class ShopItem(ShopItemBase):
    id: int

    class Config:
        from_attributes = True

# =====================
# GENETICS SCHEMAS
# =====================
class AlleleBase(BaseModel):
    name: str
    symbol: str
    dominance_level: int = 1
    effect_value: int = 0
    description: Optional[str] = None

class AlleleCreate(AlleleBase):
    gene_id: int

class Allele(AlleleBase):
    id: int
    gene_id: int

    class Config:
        from_attributes = True

class GeneBase(BaseModel):
    name: str
    trait: str
    description: Optional[str] = None

class GeneCreate(GeneBase):
    pass

class Gene(GeneBase):
    id: int
    default_allele_id: Optional[int] = None
    alleles: List['Allele'] = []

    class Config:
        from_attributes = True

class PetGeneticsBase(BaseModel):
    gene_id: int
    allele1_id: int
    allele2_id: int

class PetGeneticsCreate(PetGeneticsBase):
    pet_id: int

class PetGenetics(PetGeneticsBase):
    id: int
    pet_id: int

    class Config:
        from_attributes = True

class OffspringBase(BaseModel):
    parent1_id: int
    parent2_id: int
    child_id: int
    inheritance_notes: Optional[str] = None

class OffspringCreate(BaseModel):
    parent1_id: int
    parent2_id: int
    child_id: int
    punnett_square_data: Optional[str] = None
    inheritance_notes: Optional[str] = None

class Offspring(OffspringBase):
    id: int
    breeding_date: datetime.datetime
    punnett_square_data: Optional[str] = None

    class Config:
        from_attributes = True

class BreedingRequest(BaseModel):
    parent1_id: int
    parent2_id: int
    owner_id: int
    child_name: str
    child_species: Optional[str] = "Guinea Pig"
    child_color: Optional[str] = "Mixed"

class PunnettSquareResult(BaseModel):
    """Represents a Punnett square calculation result"""
    gene_name: str
    parent1_genotype: str
    parent2_genotype: str
    possible_offspring: List[str]
    probabilities: dict
    punnett_square: List[List[str]]

class PetStatsSchema(BaseModel):
    """Pet stats derived from genetics"""
    speed: int
    endurance: int
    genetic_score: int

    class Config:
        from_attributes = True

class BreedingOutcome(BaseModel):
    """Complete breeding outcome with inherited genetics"""
    child_id: int
    child_name: str
    child_genetics: Optional[str] = None
    punnett_squares: List[PunnettSquareResult]
    estimated_stats: dict
    inheritance_summary: str

# =====================
# FOOD SYSTEM SCHEMAS
# =====================
class FoodEffect(BaseModel):
    """Food effect structure"""
    hunger: Optional[int] = 0
    health: Optional[int] = 0
    happiness: Optional[int] = 0
    cleanliness: Optional[int] = 0

class FeedPetRequest(BaseModel):
    """Request to feed a pet"""
    item_name: str