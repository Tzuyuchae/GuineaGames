# Add to the main game file later
import pygame

###################################################################

pygame.init()
screen = pygame.display.set_mode((128, 128))
clock = pygame.time.Clock()

counter, text = 10, '10'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.USEREVENT: 
            counter -= 1
            text = str(counter).rjust(3) if counter > 0 else 'boom!'
        if e.type == pygame.QUIT: 
            run = False

    screen.fill((255, 255, 255))
    screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
    pygame.display.flip()
    clock.tick(60)

##################################################################

start_ticks=pygame.time.get_ticks() #starter tick
while mainloop: # mainloop
    seconds=(pygame.time.get_ticks()-start_ticks)/1000 #calculate how many seconds
    if seconds>10: # if more than 10 seconds close the game
        break
    print (seconds) #print how many seconds

#################################################################
# Both of these will be changed later to match other code
playingMiniGame = None
activeGuineaPigs = []

# should probably try and make a button about this 
# in a settigs tab at some point, or could just leave as 30fps
userSetFPS = 30
FPS = userSetFPS
newAging = 0


def timers (self, guineapig, time):
    None



running = True
while running:
    if playingMiniGame == False:
        clock.tick(FPS)
        newAging += 1
    
    if (newAging // 300) == 1:

        



        
#converts to minutes
newAgingMinutes = newAging / 60

#converts to months
newAgingMonths = newAgingMinutes / 5

for pig in activeGuineaPigs:
    pig.age += newAgingMonths
