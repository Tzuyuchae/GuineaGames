from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    balance = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    pets = relationship("Pet", back_populates="owner")
    inventory = relationship("Inventory", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    leaderboard = relationship("Leaderboard", back_populates="user")
    marketplace_listings = relationship("PetMarketplace", back_populates="seller")
    sales_as_seller = relationship("PetSalesHistory", foreign_keys="PetSalesHistory.seller_id", back_populates="seller")
    purchases = relationship("PetSalesHistory", foreign_keys="PetSalesHistory.buyer_id", back_populates="buyer")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    species = Column(String)
    color = Column(String)
    color_phenotype = Column(String, nullable=True)  # Visible coat color (e.g., "Brown", "Brown-Orange mix")
    hair_type = Column(String, default="short")  # "short" or "fluffy"
    age_days = Column(Integer, default=0)
    health = Column(Integer, default=100)
    happiness = Column(Integer, default=100)
    hunger = Column(Integer, default=3)
    cleanliness = Column(Integer, default=100)
    points = Column(Integer, default=0)
    genetic_code = Column(String, nullable=True)
    speed = Column(Integer, default=50)
    endurance = Column(Integer, default=50)
    rarity_score = Column(Integer, default=0)
    rarity_tier = Column(String, default="Common")
    market_value = Column(Integer, default=100)
    for_sale = Column(Integer, default=0)  # Boolean as integer for SQLite
    asking_price = Column(Integer, nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="pets")
    genetics = relationship("PetGenetics", back_populates="pet")
    offspring_parent1 = relationship("Offspring", foreign_keys="Offspring.parent1_id", back_populates="parent1")
    offspring_parent2 = relationship("Offspring", foreign_keys="Offspring.parent2_id", back_populates="parent2")
    offspring_child = relationship("Offspring", foreign_keys="Offspring.child_id", back_populates="child")
    marketplace_listing = relationship("PetMarketplace", back_populates="pet", uselist=False)
    sales_history = relationship("PetSalesHistory", back_populates="pet")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String)
    quantity = Column(Integer, default=0)

    user = relationship("User", back_populates="inventory")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    amount = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="transactions")

class MiniGame(Base):
    __tablename__ = "mini_games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    base_reward = Column(Integer, default=0)
    cooldown_sec = Column(Integer, nullable=True)

class Leaderboard(Base):
    __tablename__ = "leaderboards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="leaderboard")

class ShopItem(Base):
    __tablename__ = "shop_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String, default='food')
    cost = Column(Integer)
    description = Column(Text, nullable=True)
    effect = Column(Text, nullable=True)

# =====================
# GENETICS MODELS
# =====================
class Gene(Base):
    __tablename__ = "genes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    trait = Column(String)
    description = Column(Text, nullable=True)
    default_allele_id = Column(Integer, nullable=True)

    alleles = relationship("Allele", back_populates="gene")
    pet_genetics = relationship("PetGenetics", back_populates="gene")

class Allele(Base):
    __tablename__ = "alleles"
    id = Column(Integer, primary_key=True, index=True)
    gene_id = Column(Integer, ForeignKey("genes.id"))
    name = Column(String)
    symbol = Column(String)
    dominance_level = Column(Integer, default=1)
    effect_value = Column(Integer, default=0)
    description = Column(Text, nullable=True)

    gene = relationship("Gene", back_populates="alleles")
    pet_genetics_allele1 = relationship("PetGenetics", foreign_keys="PetGenetics.allele1_id", back_populates="allele1")
    pet_genetics_allele2 = relationship("PetGenetics", foreign_keys="PetGenetics.allele2_id", back_populates="allele2")

class PetGenetics(Base):
    __tablename__ = "pet_genetics"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    gene_id = Column(Integer, ForeignKey("genes.id"))
    allele1_id = Column(Integer, ForeignKey("alleles.id"))
    allele2_id = Column(Integer, ForeignKey("alleles.id"))

    pet = relationship("Pet", back_populates="genetics")
    gene = relationship("Gene", back_populates="pet_genetics")
    allele1 = relationship("Allele", foreign_keys=[allele1_id], back_populates="pet_genetics_allele1")
    allele2 = relationship("Allele", foreign_keys=[allele2_id], back_populates="pet_genetics_allele2")

class Offspring(Base):
    __tablename__ = "offspring"
    id = Column(Integer, primary_key=True, index=True)
    parent1_id = Column(Integer, ForeignKey("pets.id"))
    parent2_id = Column(Integer, ForeignKey("pets.id"))
    child_id = Column(Integer, ForeignKey("pets.id"))
    breeding_date = Column(DateTime, default=datetime.datetime.utcnow)
    punnett_square_data = Column(Text, nullable=True)
    inheritance_notes = Column(Text, nullable=True)

    parent1 = relationship("Pet", foreign_keys=[parent1_id], back_populates="offspring_parent1")
    parent2 = relationship("Pet", foreign_keys=[parent2_id], back_populates="offspring_parent2")
    child = relationship("Pet", foreign_keys=[child_id], back_populates="offspring_child")

# =====================
# MARKETPLACE MODELS
# =====================

class PetMarketplace(Base):
    __tablename__ = "pet_marketplace"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), unique=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    asking_price = Column(Integer)
    listed_date = Column(DateTime, default=datetime.datetime.utcnow)

    pet = relationship("Pet", back_populates="marketplace_listing")
    seller = relationship("User", back_populates="marketplace_listings")

class PetSalesHistory(Base):
    __tablename__ = "pet_sales_history"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    sale_price = Column(Integer)
    sale_date = Column(DateTime, default=datetime.datetime.utcnow)

    pet = relationship("Pet", back_populates="sales_history")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="sales_as_seller")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="purchases")