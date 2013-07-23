import  pygame,background,tasks,clazz,loop
import logging,yaml

def map_script(ch):
	if ch=='r':
		return clazz.Clazz.RIGHT
	if ch=='l':
		return clazz.Clazz.LEFT
	if ch=='u':
		return clazz.Clazz.UP
	if ch=='d':
		return clazz.Clazz.DOWN


#logging
logger = logging.getLogger("logger")
hand =  logging.StreamHandler()
logger.setLevel(logging.DEBUG)
hand.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(name)s] - %(levelname)s - %(message)s")
hand.setFormatter(formatter)
logger.addHandler(hand)
#config load
path="cnf.yml"
logger.debug("Loading config from %s"%path)
cnf=yaml.load(file(path,"r"))
cnf['script']=map(map_script,cnf['script'])
logger.debug("%s"%cnf)

#initss
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.init()

size = width,height = 1250,500
screen = pygame.display.set_mode(size)
#inits
schedulerRunning= tasks.Scheduler()
schedulerStart= tasks.Scheduler()
bg=background.BackgroundAction((255,255,255),screen)
cross=background.CrossAction("imgs/cross.png",screen)
snd=background.SoundAction(cnf['snd'])
#classes
clazzUp=clazz.Clazz(clazz.Clazz.UP,"Tongue")
clazzDown=clazz.Clazz(clazz.Clazz.DOWN,"Foot")
clazzLeft=clazz.Clazz(clazz.Clazz.LEFT,"Left hand")
clazzRight=clazz.Clazz(clazz.Clazz.RIGHT,"Ringht hand")
painterUp=clazz.ClazzPainter(screen,clazzUp,"imgs/class.png",(255,0,0),140,[])
painterDown=clazz.ClazzPainter(screen,clazzDown,"imgs/class.png",(255,0,0),140,[])
painterLeft=clazz.ClazzPainter(screen,clazzLeft,"imgs/class.png",(255,0,0),140,[])
painterRight=clazz.ClazzPainter(screen,clazzRight,"imgs/class.png",(255,0,0),140,[])
#pool=clazz.ClassPool([painterUp,painterDown,painterLeft,painterRight],cnf['script'])
pool=clazz.RandomClassPool([painterUp,painterDown,painterLeft,painterRight],20)
clazzAction=clazz.ClassAction(pool)
#idle
taskIdle=tasks.Task(cnf['durations']['idle'])
taskIdle.addAction(bg)
schedulerRunning.addTask(taskIdle)
#show fix
taskFix=tasks.Task(cnf['durations']['fixation'])
taskFix.addAction(bg)
taskFix.addAction(cross)
taskFix.addAction(snd)
schedulerRunning.addTask(taskFix)
#show class
taskClass=tasks.Task(cnf['durations']['class'])
taskClass.addAction(bg)
taskClass.addAction(cross)
taskClass.addAction(clazzAction)
schedulerRunning.addTask(taskClass)

#Pause task
msg=background.MessageAction("Press 'Any' key to start",screen)
taskStart=tasks.Task(cnf['durations']['idle'])
taskStart.addAction(bg)
taskStart.addAction(msg)
schedulerStart.addTask(taskStart)


#start the scheduler
loop.Loop(schedulerRunning,schedulerStart).loop()

