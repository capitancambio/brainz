import threading
import pygame
import math
import logging
import numpy
import scipy.io as sio

class Game(object):
    """Docstring for Game """
    G_LEFT=1
    G_RIGHT=2
    G_JUMP=3
    

    def __init__(self,cnf):
       """@todo: to be defined """
       #list of moves for the stage
       self.goal=None
       self.trials=[]
       self.classifications=[]
       self.currentClassification=[]
       self.view=None
       self.logger=logging.getLogger("logger")
       self.finished=False
       self.cnf=cnf
       self.sound= pygame.mixer.Sound(cnf['snd'])


    def setView(self,view):
            self.view=view


    def startTrial(self,bus,clazz):
        if not self.finished:
                self.view.prep=True


    def startLiveClassification(self,bus,clazz):
        if not self.finished:
                self.view.prep=False

                self.logger.debug('play start!')
                self.sound.play()
                self.logger.debug('play stop!')


                #compute the goal having the zombie position+class
                if clazz==3:#will have to stay in the same lane
                   goal=Game.G_JUMP
                elif clazz==1:
                    goal=Game.G_LEFT
                elif clazz==2:
                    goal=Game.G_RIGHT
                
                self.trials.append(clazz)
                #update the view
                self.view.setGoal(goal)
        
    def endTrial(self,bus,clazz):
        if not self.finished:
                #update trials and classification result
                self.classifications.append(self.currentClassification[-1])
                #reset goal and the current classificaiton
                self.goal=None
                self.view.zombie.move(self.currentClassification[-1])
                self.currentClassification=[]
                #update view
                self.view.setGoal(None)

    def classEvent(self,buz,clazz):
        #update the current classificaiton 
        if self.view.goal.goal!=None and clazz!=-1: 
                self.currentClassification.append(clazz)
        #self.view.update()
        
    def theEnd(self,buzz,whatever):
        self.finished=True
        self.logger.info("This is the end")
        self.saveResults()

    def getScore(self):
        hits=0
        for exp,res in zip(self.trials,self.classifications):
                if exp==res:
                        hits+=1
        return hits

    def saveResults(self):
        path=self.cnf['outputpath']+"/online_outs/%s_%s.mat"%(self.cnf['user'],self.cnf['session'])
        ypred=numpy.array(self.classifications)
	sio.savemat(path,{'ypred':ypred})


    
class GameView(object):
        """Docstring for GameView """
        
        def __init__(self,game,screen,cnf):
                self.cnf=cnf
                self.game=game
                self.zombie=Zombie(cnf,5)
                self.terrain=Terrain(cnf,20)
                self.goal=Goal(cnf,4,self.zombie)
                self.screen=screen
                self.lock=threading.Lock()
                self.state=GameViewState()
                self.state.bgcolor=cnf['game']['bg']
                self.font=cnf['game']['font']
                self.prep=False

        def setGoal(self,clazz):
                self.lock.acquire()
                if clazz==Game.G_JUMP:
                        self.goal.setGoal(self.zombie.pos)
                elif clazz==Game.G_LEFT:
                        self.goal.setGoal(self.zombie.pos-1)
                elif clazz==Game.G_RIGHT:
                        self.goal.setGoal(self.zombie.pos+1)
                else:
                        self.goal.setGoal(None)
                self.lock.release()

        def onUpdate(self):
                #paint
                #backgound
                self.lock.acquire()
                if self.game.finished:
                        self.showScore()

                else:
                        self.screen.fill(self.state.bgcolor)
                        if self.prep:
                                self.drawStatusBarPrep()
                        else:
                                self.drawStatusBar()
                        self.terrain.update(self.screen)
                        self.goal.update(self.screen)
                        self.zombie.update(self.screen)
                self.lock.release()


        def showScore(self):
                self.screen.fill(self.state.bgcolor)
                font = pygame.font.Font(self.font, 120)
                #trials msg
                surface = font.render("Game Over!", True, (10, 10, 10))
                rect = surface.get_rect()
                rect.center=(750,200)
                self.screen.blit(surface, rect)

                surface = font.render("Score: %i "%(self.game.getScore()*100), True, (10, 10, 10))
                rect = surface.get_rect()
                rect.center=(750,300)
                self.screen.blit(surface, rect)

                surface = font.render("Hit ratio: %2.1f %% "%(100*float(self.game.getScore())/len(self.game.trials)), True, (10, 10, 10))
                rect = surface.get_rect()
                rect.center=(750,350)
                self.screen.blit(surface, rect)


        def drawStatusBar(self):
                pygame.draw.rect(self.screen, self.cnf['game']['st'], (0,0,1500,100), 0)
                font = pygame.font.Font(self.font, 80)
                #trials msg
                surface = font.render("Trials: %i"%len(self.game.trials), True, (10, 10, 10))
                rect = surface.get_rect()
                rect.center=(1100,50)
                self.screen.blit(surface, rect)
                #score
                surface = font.render("Score: %i"%(self.game.getScore()*100), True, (10, 10, 10))
                rect = surface.get_rect()
                rect.center=(1300,50)
                self.screen.blit(surface, rect)
                #arrows
                img = pygame.image.load(self.cnf['game']['arrow']).convert_alpha()
                img = pygame.transform.scale(img,(50,50))

                self.drawArrow(1,img.copy())
                self.drawArrow(2,img.copy())
                self.drawArrow(3,img.copy())
                

        def drawStatusBarPrep(self):
                pygame.draw.rect(self.screen, self.cnf['game']['st'], (0,0,1500,100), 0)
                font = pygame.font.Font(self.font, 80)
                #ready msg
                surface = font.render("Get ready!", True, (10, 10, 10))
                rect = surface.get_rect()
                rect.center=(750,50)
                self.screen.blit(surface, rect)




        def drawArrow(self,direct,img):
                pixarr=pygame.PixelArray(img)
                red=0
                green=0
                #if len(self.game.currentClassification)>0:
                        #if self.game.currentClassification[-1]==direct:
                                #red=255
                #elif len(self.game.classifications)>0 and self.game.classifications[-1]==direct:
                                #green=255

                pixarr.replace((0,255,0),(red,green,0),distance=0)
                img=pixarr.surface
                del pixarr
                rect = img.get_rect()
                if direct==Game.G_RIGHT:#right
                        rect.center = (750+100,50) 
                elif direct==Game.G_LEFT:#left
                        img=pygame.transform.rotate(img,180)
                        rect.center = (750-100,50) 
                else:
                        img=pygame.transform.rotate(img,90)
                        rect.center = (750,50) 

                self.screen.blit(img,rect)	

class GameViewState:

        def __init__(self):
                self.bgcolor=None        



class Goal(object):
        """Docstring for Goal """

        def __init__(self,cnf,updateRate,zombie):
                self.cnf=cnf
                self.pics=[]
                self.tick=0
                self.step=0
                self.goal=None
                self.pos=[0,0]
                self.updateRate=updateRate
                self.__load_pics()
                self.zombie=zombie
                self.totalSteps=100
                self.dSize=20./self.totalSteps 
                self.stepSize=[]
                self.angle=0.0
                self.bomb=True
                self.lock=threading.Lock()
                
        def __load_pics(self):
                imgs=self.cnf['game']['goals'] 
                for img in imgs:
                       pic=pygame.image.load(img).convert_alpha()
                       self.pics.append(pic) 

        def setGoal(self,goal):
                self.lock.acquire()
                if goal == None:
                        self.goal==None
                elif self.goal==None:
                        self.goal=goal
                        self.step=0
                        if goal==self.zombie.pos:
                                self.img=self.pics[1].copy()
                                self.bomb=True
                        else:
                                self.img=self.pics[0].copy()
                                self.bomb=False

                        self.pos=[750+(self.goal-1)*85,110]
                        self.stepSize=[0,(700)/self.totalSteps]
                        self.angle=(self.goal-1)*0.16

                self.lock.release()

        def update(self,screen): 
               if self.goal==None:
                       return
               self.lock.acquire()


               if self.tick % self.updateRate == 0:
                      self.step+=1
                      self.pos[0]+=self.stepSize[0]
                      self.pos[1]+=self.stepSize[1]

               if not self.bomb: 
                       self.drawGoal(screen,self.pos,self.angle)
               else:
                       pos=[750-85,self.pos[1]]
                       self.drawGoal(screen,pos,-0.16)
                       pos=[750,self.pos[1]]
                       self.drawGoal(screen,pos,0)
                       pos=[750+85,self.pos[1]]
                       self.drawGoal(screen,pos,0.16)


               if self.step==self.totalSteps:
                       self.goal=None

               self.tick+=1
               self.tick=self.tick % self.updateRate
               self.lock.release()

        def drawGoal(self,screen,pos,angle):
               size=int(20.+self.dSize*self.step)
               img=self.img 
               img = pygame.transform.scale(img,(size,size))
               rect = img.get_rect()
               rect.center = (pos[0]+(angle*(pos[1]-10)),pos[1]) 
               screen.blit(img,rect)	


class Terrain(object):
        """Docstring for Terrain """

        def __init__(self,cnf,updateRate):
                """@todo: to be defined """
                self.cnf=cnf
                self.pics=[]
                self.tick=0
                self.step=0
                self.updateRate=updateRate
                self.__load_pics()

        def __load_pics(self):
                imgs=self.cnf['game']['terrain'] 
                for img in imgs:
                       pic=pygame.image.load(img).convert_alpha()
                       self.pics.append(pic) 
        
        def update(self,screen):
               if self.tick % self.updateRate == 0:
                      self.step+=1

               self.step=self.step % len(self.pics)

               img=self.pics[self.step].copy() 
               rect = img.get_rect()
               rect.x= 0
               rect.y= 100 
               screen.blit(img,rect)	
               self.tick+=1
               self.tick=self.tick % self.updateRate

class Zombie(object):
        """Docstring for Zombie """
         
        def __init__(self,cnf,updateRate):
                """@todo: to be defined """
                self.cnf=cnf
                self.pos=1
                self.nextPos=1
                self.curPos=750
                self.pics=[]
                self.jumpingPics=[]
                self.jump=False
                self.jumpStep=0
                self.tick=0
                self.updateRate=updateRate
                self.step=0
                self.__load_pics()

        def __load_pics(self):
                imgs=self.cnf['game']['c_walk'] 
                for img in imgs:
                       pic=pygame.image.load(img).convert_alpha()
                       pic=pygame.transform.scale(pic,(30,90))
                       self.pics.append(pic) 

                imgs=self.cnf['game']['c_jump'] 
                for img in imgs:
                       pic=pygame.image.load(img).convert_alpha()
                       pic=pygame.transform.scale(pic,(30,114))
                       self.jumpingPics.append(pic) 
      
        def __str__(self):
                return "[zombie curPos:%i pos:%i next:%i]"%(self.curPos,self.pos,self.nextPos)

        def move(self,mov):
                if mov==Game.G_LEFT and self.isStill():
                        if self.pos>0:
                                self.nextPos-=1
                elif mov==Game.G_RIGHT and self.isStill():
                        if self.pos<2:
                                self.nextPos+=1
                elif mov==Game.G_JUMP:
                        self.jump=True
                        self.jumpStep=1.

        def isStill(self):
                return self.curPos==750 or self.curPos==750+200 or self.curPos ==750-200

        def __move(self):
                if self.nextPos!=self.pos:
                       self.curPos+=(self.nextPos-self.pos)*5
                       if self.isStill(): 
                                self.pos=self.nextPos
                elif self.jump:
                        pass
                        self.jumpStep+=0.065
                        if self.jumpStep>=len(self.jumpingPics)*2:
                                self.jump=False

        
        def update(self,screen):
               if self.tick % self.updateRate == 0:
                      self.step+=1
               self.step=self.step % len(self.pics)
               img=None
               yAdj=0
               if not self.jump:
                        img=self.pics[self.step].copy() 

               else:
                       yAdj=5

                       idx=int(math.floor(self.jumpStep))
                       if idx>len(self.jumpingPics):
                               idx=len(self.jumpingPics)-idx%len(self.jumpingPics)
                       img=self.jumpingPics[idx-1].copy() 

               rect = img.get_rect()
               self.__move()
               rect.center = (self.curPos,800-yAdj) 
               screen.blit(img,rect)	
               self.tick+=1
               self.tick=self.tick % self.updateRate


