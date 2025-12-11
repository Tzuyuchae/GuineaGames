# frankly, at this point I'm unsure which of these I actually need, I just don't want to break anything by removing it
import random
import json
from typing import List, Dict, Tuple

import models, schemas
from pricing import RarityCalculator
from fastapi import FastAPI
from routes import users, pets, inventory, transactions, mini_games, leaderboard, genetics, marketplace

import typing
import APIClient
from sqlalchemy.orm import Session
import database
import pygame
import os
from minigame.button import Button

import homescreen import pet_dies


# --- TIME PASSING -------------------------------------------------------------------------------------------------------------------

def inc_month():
    db = database.get_db()
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
    for pet in pets:
        # if pig was already at 0 hunger, it starves
        if pet.hunger == 0:
            pet_dies(pet.name)
            
        # gpigs age and get hungrier
        pet.hunger -= 1
        pet.age_months += 1
    
        # save age as local var
        age = pet.age_months
        
        # Midsommar the old gpigs (sorry for spoilers)
        if age == 60:
            pet_dies(pet.name)
    
        # decrease stats in last 3 months
        elif age >= 57
            pet.endurance = max(1, pet.endurance - 5)
            pet.speed = max(1, pet.speed - 4)
    
        
        elif age == 3:
            # gpigs grow to full size after 3 months, start at 0 months old
            
    
        #increase points as they age (0-60 month lifespan)
        # pigs gain a total of 179 points across lifetime
        if age >= 57:
            pet.points += 10
        elif age >= 48:
            pet.points += 5
        elif age >= 36:
            pet.points += 3
        elif age >= 12:
            pet.points += 2
        elif age >= 3:
            pet.points += 1
    db.commit()
