# Add to the main game file later
import sqlite3
import pygame 

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

counter, text = 10, '10'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)

#id, owner_id,name,species,color,age_months,health,happiness,hunger,cleanliness, last_updated
def getPlayerPigs(self): 
    dict = {}
    cursor.execute("SELECT id, hunger FROM PETS")
    rows = cursor.fetchall()
    for item in rows:
        dict[item[0]] = 
    

    return dict

def inc_month(self, listAllGuineaPigs):
    
    # THIS WILL LIKELY NEED TO BE MODIFIED #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  
    for gp in listAllGuineaPigs:
        gp.hunger -= 1

def quitGame(self):

    return False     #run = False


timePassed = 0
# should probably try and make a button for FPS
# in a settigs tab at some point, or could just leave as 30fps
FPS = 30
# This variable name will probably be different in Main
gamePaused = False

playerPigs = getPlayerPigs()

run = True
while run:
    if gamePaused == False:
        clock.tick(FPS)
    for e in pygame.event.get():
        timePassed += 1
        if timePassed == 300000:        #300k ms is ~5 minutes
            timePassed = 0
            inc_month()
        if e.type == pygame.USEREVENT:
            counter -= 1
            text = str(counter).rjust(3) if counter > 0 else 'boom!'
        if e.type == pygame.QUIT:
            run = quitGame()

    screen.fill((255, 255, 255))
    screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
    pygame.display.flip()
    clock.tick(60)

sqliteConnection.commit()
sqliteConnection.close()

##################################################################

mainloop = True
start_ticks=pygame.time.get_ticks() #starter tick
while mainloop: # mainloop
    seconds=(pygame.time.get_ticks()-start_ticks)/1000 #calculate how many seconds
    if seconds>10: # if more than 10 seconds close the game
        break
    print (seconds) #print how many seconds

