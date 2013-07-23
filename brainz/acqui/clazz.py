from acqui.tasks import Action
import pygame,math,random
import logging 
import yaml
class Clazz(yaml.YAMLObject):
	UP=4
	DOWN=3
	LEFT=1
	RIGHT=2
	yaml_tag=u'!clazz'
	def __init__(self,orientation,mesg,img,color):
		self.orientation=orientation
		self.mesg=mesg
		self.img=img
		self.color=color
	def mark():
		def fget(self):
			return self.orientation

class ClazzPainter:
	COLOR_KEY=(255,255,255)

	def __init__(self,screen,clazz,radious,mesgWriter):
		self.clazz=clazz
		self.orientation=clazz.orientation
		self.img=pygame.image.load(self.clazz.img).convert_alpha()
		self.screen=screen
		self.mesgWriter=mesgWriter
		#self.img=pygame.rotate(self.img,90*self.orientation)
		pixarr=pygame.PixelArray(self.img)
		pixarr.replace(ClazzPainter.COLOR_KEY,self.clazz.color,distance=0)
		self.img=pixarr.surface
		self.rect=self.img.get_rect()
		centre=(math.ceil(screen.get_size()[0]/2-self.rect.width/2), math.ceil(screen.get_size()[1]/2-self.rect.height/2))
		self.rect.move_ip(centre)
		if self.orientation == Clazz.UP  :
			self.rect.move_ip(0,-radious)
		if self.orientation == Clazz.DOWN:
			self.rect.move_ip(0,radious)
		if self.orientation == Clazz.LEFT:
			self.rect.move_ip(-radious,0)

		if self.orientation == Clazz.RIGHT:
			self.rect.move_ip(radious,0)
	def paint(self):
		self.screen.blit(self.img,self.rect)	

	def clazz():
		def fget(self):
			return self.clazz

class ClassPool:
	"""
		clazzes : the classes to show 
		script: a list of orientations (Clazz.UP ... ) to show 
	"""
	def __init__(self,clazzPainters,script):
		self.clazzes={}
		for clazz in clazzPainters:
			self.clazzes[clazz.orientation]=clazz
		self.script=[]
		for sc in script:
			self.script.append(self.clazzes[sc])

		self.it=-1;
		self.logger = logging.getLogger("logger")

	def next(self):
		if self.it <len(self.script):
			self.it+=1

			self.logger.debug("Orientation %i",self.script[self.it].orientation)
			return self.script[self.it]
		else:
			return False
	def current(self):
		return self.script[self.it]
	def reset(self):
		self.it=-1

class RandomClassPool (ClassPool):
	def __init__(self,clazzPainters,lenght):
		self.logger=logging.getLogger("logger")
		clazzes={}
		for clazz in clazzPainters:
			clazzes[clazz.orientation]=clazz
		script=[]
		keys=clazzes.keys()
		#change to make the number of classes even
		for i in range(1,lenght):
			#script.append(keys[random.randint(0,len(keys)-1)])
			script.append(keys[i%len(keys)])
		random.shuffle(script)	
		ClassPool.__init__(self,clazzPainters,script)
	
class ClassAction (Action):
	def __init__(self,classPool):
		self.pool=classPool

	def onStart(self):
		if self.pool.next()==False:
			raise RuntimeError
	def onUpdate(self):
		self.pool.current().paint()
	def onReset(self):
		self.pool.reset()
