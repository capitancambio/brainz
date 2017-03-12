import pygame
import actions
import tasks
import clazz
import logging
import yaml
import launcher


def map_script(ch):
    if ch == 'r':
        return clazz.Clazz.RIGHT
    if ch == 'l':
        return clazz.Clazz.LEFT
    if ch == 'u':
        return clazz.Clazz.UP
    if ch == 'd':
        return clazz.Clazz.DOWN


# logging
logger = logging.getLogger("logger")
hand = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
hand.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(name)s] - %(levelname)s - %(message)s")
hand.setFormatter(formatter)
logger.addHandler(hand)
# config load
path = "cnf.yml"
logger.debug("Loading config from %s" % path)
cnf = yaml.load(file(path, "r"))
logger.debug("%s" % cnf)

# initss
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.init()

size = width, height = 1250, 500
screen = pygame.display.set_mode(size)
# inits
schedulerRunning = tasks.Scheduler()
schedulerStart = tasks.Scheduler()
bg = actions.BackgroundAction((255, 255, 255), screen)
cross = actions.CrossAction("imgs/cross.png", screen)
snd = actions.SoundAction(cnf['snd'])

print cnf["classes"]
# classes
clazzUp = cnf["classes"]["tongue"]
clazzDown = cnf["classes"]["foot"]
clazzRight = cnf["classes"]["right"]
clazzLeft = cnf["classes"]["left"]

painterUp = clazz.ClazzPainter(
    screen, clazzUp,  140, None)
painterDown = clazz.ClazzPainter(
    screen, clazzDown, 140, None)
painterLeft = clazz.ClazzPainter(
    screen, clazzLeft, 140, None)
painterRight = clazz.ClazzPainter(
    screen, clazzRight,  140, None)
# pool=clazz.ClassPool([painterUp,painterDown,painterLeft,painterRight],cnf['script'])
pool = clazz.RandomClassPool(
    [painterUp, painterDown, painterLeft, painterRight], 20)
clazzAction = clazz.ClassAction(pool)
# idle
taskIdle = tasks.Task(
    launcher.RangedDurationProvider(cnf['durations']['idle']))
taskIdle.addAction(bg)
schedulerRunning.addTask(taskIdle)
# show fix
taskFix = tasks.Task(launcher.DurationProvider(
    cnf['durations']['fixation']))
taskFix.addAction(bg)
taskFix.addAction(cross)
taskFix.addAction(snd)
schedulerRunning.addTask(taskFix)
# show class
taskClass = tasks.Task(launcher.DurationProvider(
    cnf['durations']['class']))
taskClass.addAction(bg)
taskClass.addAction(cross)
taskClass.addAction(clazzAction)
schedulerRunning.addTask(taskClass)

# Pause task
msg = actions.MessageAction("Press 'Any' key to start", screen)
taskStart = tasks.Task(launcher.RangedDurationProvider(
    cnf['durations']['idle']))
taskStart.addAction(bg)
taskStart.addAction(msg)
schedulerStart.addTask(taskStart)


# start the scheduler
tasks.Loop(schedulerRunning, schedulerStart).loop()
