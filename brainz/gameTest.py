import pygame
import yaml
import game as g
#load conf and init pygame
path = 'brainz.yml'
cnf = yaml.load(file(path, 'r'))
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.init()
size = (width, height) = (cnf['disp']['w'], cnf['disp']['h'])
screen = pygame.display.set_mode(size)

game=g.Game()
view=g.GameView(game,screen,cnf)
game.setView(view)

running=True
while running:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    print 'KEY %s'%event.key
                    if( event.key==276):
                            game.classEvent([],game.G_LEFT)
                    elif ( event.key==275):
                            game.classEvent([],game.G_RIGHT)
                    elif ( event.key==273):
                            game.classEvent([],game.G_JUMP)
                    elif ( event.key==97):
                            game.startLiveClassification(None,game.G_JUMP) 
                    elif ( event.key==115):
                            game.startLiveClassification(None,game.G_LEFT) 
                    elif ( event.key==100):
                            game.startLiveClassification(None,game.G_RIGHT) 
                    elif ( event.key==32):
                            game.endTrial(None,game.G_RIGHT) 
                    elif ( event.key==113):
                            game.startTrial(None,game.G_RIGHT) 

                     
        game.view.onUpdate()
        pygame.display.flip()

