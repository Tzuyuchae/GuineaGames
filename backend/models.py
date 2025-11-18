from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    pets = relationship("Pet", back_populates="owner")

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    species = Column(String)
    color = Column(String)
    age_months = Column(Integer, default=0)
    health = Column(Integer, default=100)
    happiness = Column(Integer, default=100)
    hunger = Column(Integer, default=100)
    cleanliness = Column(Integer, default=100)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="pets")