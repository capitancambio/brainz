#!/usr/bin/env python
import logging
import yaml
import os
import sys
import pygame
import fake


from matlab import BCIConn, BCIConnDataBuffer
from conn.biosemi import BiosemiClient, DataPoster, DataBuilder
from data.bus import DataBus
from data.writer import DataWriter, DataPath, DataAppender
import acqui.tasks as tasks
import acqui.actions as actions
import acqui.clazz as clazz
import acqui.launcher as launcher
import globals

#logging
logger = logging.getLogger("logger")
hand = logging.StreamHandler()
hand2 = logging.FileHandler("brainz.txt", mode='a', encoding=None, delay=False)
logger.setLevel(logging.DEBUG)
hand.setLevel(logging.DEBUG)
hand2.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(name)s] - %(levelname)s - %(message)s")
hand.setFormatter(formatter)
hand2.setFormatter(formatter)
logger.addHandler(hand)
logger.addHandler(hand2)
#globals

def buildBiosemiConn(cnf,dataBuilder):
    """@todo: Docstring for buildBiosemiConn

    :arg1: @todo
    :returns: @todo

    """
    globals.FAKE_IT
    bioConn=None
    if not globals.FAKE_IT:
        bioConn = BiosemiClient(cnf['host'],cnf['port'],dataBuilder)
    else:
        bioConn=fake.FakeBioSemi(dataBuilder)
    return bioConn

def buildBCIConn(user):
    """@todo: Docstring for buildBiosemiConn

    :arg1: @todo
    :returns: @todo

    """
    bciConn=None
    if not globals.FAKE_IT:
        bciConn = BCIConn(int(user))
    else:
        bciConn=fake.FakeBCIConn()
    return bciConn

if len(sys.argv) != 2:
	print "REMEMBER THE USER!!"
	raise RuntimeError

user = sys.argv[1]
#load conf
path = "brainz.yml"
logger.debug("Loading config from %s"%path)
cnf = yaml.load(file(path,"r"))

trialDur = (cnf['durations']['fixation']+cnf['durations']['class'])/1000*cnf['fs']

logger.info("Initialising...")
logger.info('trial duration set to %i'%trialDur)



#bioSemi connection
dataBuilder = DataBuilder(cnf['tcpLen'],cnf['channels'], cnf['samples'])
bioConn=buildBiosemiConn(cnf,dataBuilder)
bioConn.init()

logger.info("BiosemiConn up")
##buffering stuff
dBus = DataBus()
dPoster = DataPoster(globals.BUS,bioConn)
##we dont want to accumulate things in the tcp buff
dPoster.start()

logger.info("DataPoster configured")

path = DataPath(cnf['outputpath']+os.sep+user,'dx%s.mat','dy%s.mat')
path.clear()

dataAppender = DataAppender(path,trialDur)
dataWriter = DataWriter(dataAppender)
globals.BUS.subscribe(DataPoster.DATA_EVENT,dataWriter.notify)
globals.BUS.subscribe(globals.TRIAL_START_EVENT,dataWriter.startWriting)
globals.BUS.subscribe(globals.TRIAL_STOP_EVENT,dataWriter.stopWriting)
logger.info("Data writer registered")
##connection with matlab
bciConn=buildBCIConn(int(user))
bciConn.start()
bciConnBuffer=BCIConnDataBuffer(bciConn)
globals.BUS.subscribe(DataPoster.DATA_EVENT,bciConnBuffer.notify)
globals.BUS.subscribe(globals.TRIAL_START_EVENT,bciConnBuffer.startTrial)
globals.BUS.subscribe(globals.TRIAL_STOP_EVENT,bciConnBuffer.stopTrial)
logger.info("BCI conn registered")
#test
#ticker=fake.TrialTicker()
#ticker.start()


dPoster.stop()
dPoster.join()
##appending and writing data


##init Brainz!
brainz=BrainzLauncher()
brainz.start()

#bioConn.close()
#bciConn.close()
#dPoster.stop()
#dPoster.join()



class BrainzLauncher(object):
    """Docstring for BrainzLauncher """

    def __init__(self,cnf):
        """@todo: to be defined """
        self.cnf=cnf

    def launch(self):
        pass

    def _init_pygame(self):
		self.logger.debug("Pygame init")
		pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
		pygame.init()
		size = width,height =self.cnf['disp']['w'],self.cnf['disp']['h']
		self.screen = pygame.display.set_mode(size)


    def _init_scheduler(self):
        self.logger.debug("Scheduler init")
        #inits
        self.schedulerRunning= tasks.Scheduler()
        self.schedulerStart= tasks.Scheduler()
        #here goes the the game state and stuff
        #gameAction=GameAction(cnf)
        bg=actions.BackgroundAction((255,255,255),self.screen)
        cross=actions.CrossAction("imgs/cross.png",self.screen)
        snd=actions.SoundAction(self.cnf['snd'])
        painters=[ clazz.ClazzPainter( self.screen,cl,140,[]) for cl in self.cnf['classes']]
        pool=clazz.RandomClassPool(painters,self.cnf['trials'])
        clazzAction=clazz.ClassAction(pool)
        dStart=actions.DataWriteStartAction(self.dataWriter)
        dStop=actions.DataWriteStopAction(self.dataWriter,pool)
        #idle
        taskIdle=tasks.Task(launcher.duration_provider_factory(self.cnf['durations']['idle']))
        taskIdle.addAction(bg)
        self.schedulerRunning.addTask(taskIdle)
        #show fix
        taskFix=tasks.Task(launcher.duration_provider_factory( self.cnf['durations']['fixation'] ))
        taskFix.addAction(bg)
        taskFix.addAction(cross)
        taskFix.addAction(snd)
        taskFix.addAction(dStart)
        self.schedulerRunning.addTask(taskFix)
        #show class
        taskClass=tasks.Task(launcher.duration_provider_factory( self.cnf['durations']['class']+300 ))
        taskClass.addAction(bg)
        taskClass.addAction(cross)
        taskClass.addAction(dStop)
        taskClass.addAction(clazzAction)
        self.schedulerRunning.addTask(taskClass)

        #Pause task
        msg=actions.MessageAction("Loading...",self.screen)
        taskStart=tasks.Task(launcher.DurationProvider(500))
        taskStart.addAction(bg)
        taskStart.addAction(msg)
        self.schedulerStart.addTask(taskStart)

