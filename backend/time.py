# Add to the main game file later
import pygame

clock = pygame.time.Clock()

# Both of these will be changed later to match other code
playingMiniGame = None
activeGuineaPigs = []

# should probably try and make a button about this 
# in a settigs tab at some point, or could just leave as 30fps
userSetFPS = 30
FPS = userSetFPS
newAging = 0

running = True
while running:
    if playingMiniGame == True:
        clock.tick(0)
    else:
        clock.tick(FPS)
        newAging += 1
        
#converts to minutes
newAgingMinutes = newAging / 60

#converts to months
newAgingMonths = newAgingMinutes / 5

for pig in activeGuineaPigs:
    pig.age += newAgingMonths
