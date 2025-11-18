from pydantic import BaseModel
from typing import Optional, List
import datetime

class PetBase(BaseModel):
    name: str
    species: str
    color: str

class PetCreate(PetBase):
    pass

class Pet(PetBase):
    id: int
    health: int
    speed: int
    hunger: int
    endurance: int
    last_updated: datetime.datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    pets: List[Pet] = []

    class Config:
        orm_mode = True