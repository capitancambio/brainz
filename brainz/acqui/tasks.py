import logging
import pygame

class Scheduler:
    """ list of tasks, keeps track of the current track and changes it
    depending of the amount of time spent from the previous calls

    Behaves as a circular list
    """
    def __init__(self):
        self.tasks=[];
        self.current=-1;
        self.currentTime=0;
        self.currentDuration=0;
        self.logger = logging.getLogger("logger")

    def addTask(self,task):
        self.tasks.append(task)

    def reset(self):
        self.current=-1;
        self.currentTime=0;
        self.currentDuration=0;
        for t in self.tasks:
            t.reset()
            def changeContext(self):
                cur=self.current
                nxt=(self.current+1)%len(self.tasks)
                if cur!=-1:
                    self.tasks[cur].stop()
                    self.currentDuration=self.tasks[nxt].getDuration()
                    self.tasks[nxt].start()
                    self.current=nxt

    def tick(self,millis):
        self.currentTime+=millis
        if self.currentTime>=self.currentDuration:
            self.currentTime=0;
            self.changeContext()

        self.tasks[self.current].update()


class Task:

    """ Defines a task of given duration, every task contains some pre actions
    and post actions to be called when it starts and it ends
    """
    def __init__(self,durationProvider):
        #duration is a provider
        self.durationProvider=durationProvider
        self.actions=[]
        self.logger = logging.getLogger("logger")
        self.logger.debug("prov type %s"%self.durationProvider.__class__.__name__)
        """ milliseconds! """
        def getDuration(self):
            return self.durationProvider.get()

    def addAction(self,action):
        self.actions.append(action)
        return self


    def start(self):
        for action in self.actions:
            action.onStart()

    def stop(self):
        for action in self.actions:
            action.onStop()

    def update(self):
        for action in self.actions:
            action.onUpdate()
            def reset(self):
                for action in self.actions:
                    action.onReset()

class Action(object):
    def onStart(self):
        pass
    def onUpdate(self):
        pass
    def onStop(self):
        pass
    def onReset(self):
        pass

class Loop:
    IDLE=0;
    RUNNING=1;
    def __init__(self,schedulerRunning,schedulerIdle):
        self.logger=logging.getLogger("logger")
        self.state=Loop.IDLE
        self.schedulerRunning=schedulerRunning
        self.schedulerIdle=schedulerIdle
        self.nextState=-1;



    def loop(self):
        clk=pygame.time.Clock()
        clk.tick
        self.schedulerIdle.changeContext()
        running=True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running=False
                elif event.type == pygame.KEYDOWN:
                    self.logger.debug("KEY %s",event.key)
                elif event.key==27:
                    running=False
                elif self.state==Loop.IDLE:
                    self.nextState=Loop.RUNNING
                elif self.state==Loop.RUNNING:
                    #self.nextState=Loop.IDLE
                    pass

            if self.nextState==Loop.RUNNING:
                clk=pygame.time.Clock()
                clk.tick
                self.schedulerRunning.reset()
                self.schedulerRunning.changeContext()
                self.nextState=-1
                self.state=Loop.RUNNING
                if self.nextState==Loop.IDLE:
                    clk=pygame.time.Clock()
                    clk.tick
                    self.schedulerIdle.reset()
                    self.schedulerIdle.changeContext()
                    self.nextState=-1
                    self.state=Loop.IDLE
                elif self.state==Loop.RUNNING:
                    self.schedulerRunning.tick(clk.tick())
                elif self.state==Loop.IDLE:
                    self.schedulerIdle.tick(clk.tick())

                pygame.display.flip()

