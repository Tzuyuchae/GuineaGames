# Add to the main game file later
import sqlite3
import pygame 
import datetime
from models import Pets

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
# id, owner_id, name, species, color, age_months, health, speed, hunger, endurance, score, sizeScalar, last_updated
def readInGPigs(self): 
    gpigs = {}
    cursor.execute("SELECT * FROM PETS")
    rows = cursor.fetchall()
    for row in rows:
        #newPet doesn't take in datetime as an arg, it instead runs datetime.datetime inside the method
        gpig = Pets.newPet(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
        gpigs[row[0]] = gpig

    return gpigs

def newPig():
    None


def inc_month(self, gpigs):
    for i in gpigs.items():
        # if gpig was already at 0 hunger, they starve
        if i.get_age_months == 0:
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
        vals = i.get_all_info()
        cursor.execute(f"""
            UPDATE PETS
            SET name = {vals[1]}, age_months = {vals[2]}, health = {vals[3]}, speed = {vals[4]}, hunger = {vals[5]}, endurance = {vals[6]}, score = {vals[7]}, sizeScalar = {vals[8]}, last_updated = {vals[9]}, 
            WHERE PETS.id = {vals[0]}
            """
        )
    sqliteConnection.commit()
    sqliteConnection.close()
    return False





######## THIS HAS BEEN COPIED INTO MAIN.PY PYGAME LOOP WHERE RELEVANT ###################################################

# timePassed = 0
# # should probably try and make a button for FPS
# # in a settigs tab at some point, or could just leave as 30fps
# FPS = 30
# # This variable name will probably be different in Main
# gamePaused = False

# playerPigs = getPlayerPigs()

# run = True
# while run:
#     if gamePaused == False:
#         clock.tick(FPS)
#     for e in pygame.event.get():
#         timePassed += 1
#         if timePassed == 300000:        #300k ms is ~5 minutes
#             timePassed = 0
#             inc_month()
#         if e.type == pygame.USEREVENT:
#             counter -= 1
#             text = str(counter).rjust(3) if counter > 0 else 'boom!'
#         if e.type == pygame.QUIT:
#             run = closingUpdate(playerPigs)

#     screen.fill((255, 255, 255))
#     screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
#     pygame.display.flip()
#     clock.tick(60)

# sqliteConnection.commit()
# sqliteConnection.close()

##################################################################

# mainloop = True
# start_ticks=pygame.time.get_ticks() #starter tick
# while mainloop: # mainloop
#     seconds=(pygame.time.get_ticks()-start_ticks)/1000 #calculate how many seconds
#     if seconds>10: # if more than 10 seconds close the game
#         break
#     print (seconds) #print how many seconds

