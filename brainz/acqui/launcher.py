import threading
import logging
import pygame
import random
import acqui.tasks as tasks
import acqui.actions as actions
import acqui.clazz as clazz
class AcquiLauncher(threading.Thread):
	"""docstring for AcquiLauncher"""
	def __init__(self,cnf,dataWriter):
		super(AcquiLauncher, self).__init__()
		self.logger=logging.getLogger("logger")
		self.cnf=cnf
		self.dataWriter=dataWriter
		self.init_pygame()
		self.init_scheduler()

	
	def init_pygame(self):
		self.logger.debug("Pygame init")
		pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
		pygame.init()
		size = width,height =self.cnf['disp']['w'],self.cnf['disp']['h']
		self.screen = pygame.display.set_mode(size)
	
	def init_scheduler(self):
		self.logger.debug("Scheduler init")
		#inits
		self.schedulerRunning= tasks.Scheduler()
		self.schedulerStart= tasks.Scheduler()
		bg=actions.BackgroundAction((255,255,255),self.screen)
		cross=actions.CrossAction("imgs/cross.png",self.screen)
		snd=actions.SoundAction(self.cnf['snd'])
		painters=[ clazz.ClazzPainter( self.screen,cl,140,[]) for cl in self.cnf['classes']]
		pool=clazz.RandomClassPool(painters,self.cnf['trials'])
		clazzAction=clazz.ClassAction(pool)
		dStart=actions.DataWriteStartAction(self.dataWriter)
		dStop=actions.DataWriteStopAction(self.dataWriter,pool)
		#idle
		taskIdle=tasks.Task(duration_provider_factory(self.cnf['durations']['idle']))
		taskIdle.addAction(bg)
		self.schedulerRunning.addTask(taskIdle)
		#show fix
		taskFix=tasks.Task(duration_provider_factory( self.cnf['durations']['fixation'] ))
		taskFix.addAction(bg)
		taskFix.addAction(cross)
		taskFix.addAction(snd)
		taskFix.addAction(dStart)
		self.schedulerRunning.addTask(taskFix)
		#show class
		taskClass=tasks.Task(duration_provider_factory( self.cnf['durations']['class']+300 ))
		taskClass.addAction(bg)
		taskClass.addAction(cross)
		taskClass.addAction(dStop)
		taskClass.addAction(clazzAction)
		self.schedulerRunning.addTask(taskClass)

		#Pause task
		msg=actions.MessageAction("Press 'Any' key to start",self.screen)
		taskStart=tasks.Task(DurationProvider(500))
		taskStart.addAction(bg)
		taskStart.addAction(msg)
		self.schedulerStart.addTask(taskStart)

	def run(self):
		tasks.Loop(self.schedulerRunning,self.schedulerStart).loop()

class DurationProvider(object):
	"""docstring for DurationProvider"""
	def __init__(self,duration):
		super(DurationProvider, self).__init__()
		self.duration = duration
		self.logger=logging.getLogger("logger")

	def get(self):
		return self.duration	
	

class RangedDurationProvider(object):
	"""docstring for DurationProvider"""
	def __init__(self,limits):
		super(RangedDurationProvider, self).__init__()
		self.logger=logging.getLogger("logger")
		self.limits = limits

	def get(self):
		d=random.uniform(self.limits[0],self.limits[1])
		self.logger.debug("d %f",d)
		return d

def duration_provider_factory(duration):
	"""docstring for duration_provider_factory"""
	logging.getLogger("logger").debug("duration %s"%duration.__class__.__name__)
	if type(duration) is tuple:
		return RangedDurationProvider(duration)
	else:
		return DurationProvider(duration)

def map_script(ch):
	if ch=='r':
		return clazz.Clazz.RIGHT
	if ch=='l':
		return clazz.Clazz.LEFT
	if ch=='u':
		return clazz.Clazz.UP
	if ch=='d':
		return clazz.Clazz.DOWN
