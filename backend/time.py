import sqlite3
import pygame
import datetime
from models import Pet


sqliteConnection = sqlite3.connect("database.py")
cursor = sqliteConnection.cursor()


# This logic will probably need to be literally copied into the main doc
# once its up and functional

###################################################################


# create list of gpigs
# fix aging functionality


pygame.init()
screen = pygame.display.set_mode((128, 128))
clock = pygame.time.Clock()


# pigs are stored as follow in DB:

#0-9: id, owner_id, name, species, color, color_phenotype, hair_type, age_months, health, happiness
#10-19: hunger, cleanliness, points, genetic_code, speed, endurance, rarity_score, rarity_tier, market_value, for_sale
#20-21: asking_price, last_updated

def readInGPigs(self):
    sqliteConnection = sqlite3.connect("database.py")
    cursor = sqliteConnection.cursor()

    gpigs = {}
    cursor.execute("SELECT * FROM pets")
    rows = cursor.fetchall()
    for row in rows:
        #newPet doesn't take in datetime as an arg, it instead runs datetime.datetime inside the method
        gpig = Pet.newPet(row)
        gpigs[row[0]] = gpig

    return gpigs


def inc_month(self, gpigs):
    for i in gpigs.items():
        # if gpig was already at 0 hunger, they starve
        if gpigs[i].get_age_months == 0:
            # display message
            gpigs.pop(i)

        # gpigs age and get hungrier
        gpigs[i].inc_age_months()
        age = gpigs[i].get_age_months()

        # Midsommar the old gpigs (sorry for spoilers)
        if age == 60:
            # display message
            gpigs.pop(i)

        # decrease stats in last 3 months
        elif age == 57:
            gpigs[i].speed_decrease_old_pigs()
            gpigs[i].endurance_decrease_old_pigs()

        # gpigs grow to full size after 3 months, start at 0 months old
        elif age == 3:
            gpigs[i].set_size_full_grown()
       
        #increase score as they age (0-60 month lifespan)
        # pigs gain a total of 179 points across lifetime
        if age >= 57:
           gpigs[i].add_to_score(10)
        elif age >= 48:
            gpigs[i].add_to_score(5)
        elif age >= 36:
            gpigs[i].add_to_score(3)
        elif age >= 12:
            gpigs[i].add_to_score(2)
        elif age >= 3:
            gpigs[i].add_to_score(1)
    return gpigs


def closingUpdate(self, pigs):
    for i in pigs.items():
        vals = pigs[i].get_all_info()
        cursor.execute(f"""
            UPDATE pets
            SET name = {vals[2]}, 
            age_months = {vals[7]}, 
            hair_type = {vals[6]},
            health = {vals[8]}, 
            hunger = {vals[10]}, 
            points = {vals[12]},
            speed = {vals[14]}, 
            endurance = {vals[15]}, 
            rarity_score = {vals[16]},
            rarity_tier = {vals[17]},
            sizeScalar = {vals[8]}, 
            market_value = {vals[18]},
            for_sale = {vals[19]},
            asking_price = {vals[20]},
            last_updated = {vals[21]},
            WHERE pets.id = {vals[0]}
            """
        )
    sqliteConnection.commit()
    sqliteConnection.close()
    return False

running = True
while running:
    timePassed += 1
    if timePassed == 300:        #300 seconds is 5 minutes
        timePassed = 0
        inc_month(gpigs)

