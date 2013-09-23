#!/usr/bin/python
# -*- coding: utf-8 -*-
import acqui.tasks as tasks
import acqui.actions as actions
import pygame
import acqui.launcher as launcher
import logging
import game as g
import random
import globals


class BrainzLauncher(object):

    """Docstring for BrainzLauncher """

    def __init__(self, cnf,generator):
        """@todo: to be defined """

        self.cnf = cnf
        self.logger = logging.getLogger('logger')
        self.generator=generator
        self._init_pygame()
        self._init_scheduler()

    def launch(self):
        pass

    def run(self):
        tasks.Loop(self.schedulerRunning, self.schedulerStart).loop()

    def _init_pygame(self):
        self.logger.debug('Pygame init')
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.init()
        size = (width, height) = (self.cnf['disp']['w'], self.cnf['disp']['h'])
        self.screen = pygame.display.set_mode(size)

    def _init_scheduler(self):
        self.logger.debug('Scheduler init')

        # inits

        self.schedulerRunning = tasks.Scheduler()
        self.schedulerStart = tasks.Scheduler()
        game=g.Game(self.cnf)
        globals.BUS.subscribe(globals.TRIAL_START_EVENT,game.startTrial)
        globals.BUS.subscribe(globals.TRIAL_STOP_EVENT,game.endTrial)
        globals.BUS.subscribe(globals.CLASS_EVENT,game.classEvent)
        globals.BUS.subscribe(globals.THE_END,game.theEnd)
        view=g.GameView(game,self.screen,self.cnf)
        game.setView(view)
        # here goes the the game state and stuff
        gameAction=GameAction(game)
        generator=self.generator
        startTrial=StartTrialAction(generator,globals.BUS,game)
        startClassifiying=StartLiveClassificationAction(generator,game)
        stopTrial=StopTrialAction(generator,globals.BUS)
        #during game tasks
        #pause
        waitTask=tasks.Task(launcher.DurationProvider(int(self.cnf['game']['idle_time'])))
        waitTask.addAction(gameAction)
        #start trial
        stTrialTask=tasks.Task(launcher.DurationProvider(int(self.cnf['game']['start_gap_time'])))
        stTrialTask.addAction(startTrial)
        stTrialTask.addAction(gameAction)
        #start classifying
        stClassTask=tasks.Task(launcher.DurationProvider(int(self.cnf['game']['class_time'])))
        stClassTask.addAction(startClassifiying)
        stClassTask.addAction(gameAction)
        #stop trial
        stopTrialTask=tasks.Task(launcher.DurationProvider(int(self.cnf['game']['stop_time'])))
        stopTrialTask.addAction(stopTrial)
        stopTrialTask.addAction(gameAction)
        #populate running scheduler
        self.schedulerRunning.addTask(waitTask)
        self.schedulerRunning.addTask(stTrialTask)
        self.schedulerRunning.addTask(stClassTask)
        self.schedulerRunning.addTask(stopTrialTask)

        # Pause task

        msg = actions.MessageAction('Brainz!', self.screen)
	bg=actions.BackgroundAction((255,255,255),self.screen)
        taskStart = tasks.Task(launcher.DurationProvider(20))
        taskStart.addAction(bg)
        taskStart.addAction(msg)
        self.schedulerStart.addTask(taskStart)


class GameAction(actions.Action):
        """Docstring for GameAction """

        def __init__(self,game):
               """@todo: to be defined """
               self.game=game

        def onStart(self):
                self.game.view.onUpdate()

        def onUpdate(self):
                self.game.view.onUpdate()

        def onStop(self):
                self.game.view.onUpdate()


class TrialGenerator(object):
        """Docstring for TrialGenerator """

        def __init__(self,total):
                """@todo: to be defined """
                self.cur=0
                self.count=0
                self.total=total

        def next(self,position):
                if self.count>=self.total:
                        return False
                possible=[]
                #to have an even prob of each class
                if position==0:
                        possible=[g.Game.G_JUMP,g.Game.G_RIGHT,g.Game.G_RIGHT]
                elif position==1:
                        possible=[g.Game.G_JUMP,g.Game.G_RIGHT,g.Game.G_LEFT]
                else:
                        possible=[g.Game.G_JUMP,g.Game.G_LEFT,g.Game.G_LEFT]
                self.cur=random.choice(possible)
                self.count+=1
                return self.cur

        def current(self):
                return self.cur

class StartTrialAction(tasks.Action):

	def __init__(self,generator,bus,game):
                self.bus=bus
                self.game=game
                self.generator=generator

	def onStart(self):
		if self.generator.next(self.game.view.zombie.pos)==False:
                        globals.BUS.publish(globals.THE_END,"")
                else:
                        globals.BUS.publish(globals.TRIAL_START_EVENT,self.generator.current())

class StopTrialAction(tasks.Action):

	def __init__(self,generator,bus):
                self.bus=bus
                self.generator=generator

	def onStart(self):
                globals.BUS.publish(globals.TRIAL_STOP_EVENT,self.generator.current())

class StartLiveClassificationAction(tasks.Action):
	def __init__(self,generator,game):
                self.game=game
                self.generator=generator

	def onStart(self):
                self.game.startLiveClassification(None,self.generator.current())

class TrainingTrialGenerator(object):
        """Docstring for TrialGenerator """

        def __init__(self,sequence):
                """@todo: to be defined """
                self.count=-1
                self.sequence=sequence
                self.logger=logging.getLogger("logger")
                self.position=0

        def next(self,position):
                print len(self.sequence)
                self.position
                if self.count==len(self.sequence)-1:
                        print "END!!!"
                        return False
                self.count+=1
                return self.current() 

        def current(self):
                print "current"
                print len(self.sequence)
                self.logger.debug("count %i class %i",self.count,self.sequence[ self.count ])
                return self.sequence[ self.count ]
