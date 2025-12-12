from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
try:
    # Try importing the new filename
    from backend.db_connect import Base
except ImportError:
    from db_connect import Base

import datetime

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
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
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    species = Column(String)
    # ... (rest of Pet columns)
    
    owner = relationship("User", back_populates="pets")
    # ... (rest of Pet relationships)

class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String)
    quantity = Column(Integer, default=0)

    user = relationship("User", back_populates="inventory")

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    amount = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="transactions")

class MiniGame(Base):
    __tablename__ = "mini_games"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    base_reward = Column(Integer, default=0)
    cooldown_sec = Column(Integer, nullable=True)

class Leaderboard(Base):
    __tablename__ = "leaderboards"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="leaderboard")

class ShopItem(Base):
    __tablename__ = "shop_items"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
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
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    # ... (rest of Gene columns and relationships)

class Allele(Base):
    __tablename__ = "alleles"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    # ... (rest of Allele columns and relationships)

class PetGenetics(Base):
    __tablename__ = "pet_genetics"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    # ... (rest of PetGenetics columns and relationships)

class Offspring(Base):
    __tablename__ = "offspring"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    # ... (rest of Offspring columns and relationships)

# =====================
# MARKETPLACE MODELS
# =====================

class PetMarketplace(Base):
    __tablename__ = "pet_marketplace"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    # ... (rest of PetMarketplace columns and relationships)

class PetSalesHistory(Base):
    __tablename__ = "pet_sales_history"
    __table_args__ = {'extend_existing': True}  # <--- FIX APPLIED
    # ... (rest of PetSalesHistory columns and relationships)