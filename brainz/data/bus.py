import threading
import numpy as np
import logging

class DataBus(object):
	"""Passes the data to all the registered observers"""
	def __init__(self):
		super(DataBus, self).__init__()
		self.listeners=[]
		self.logger=logging.getLogger("logger")

	def register(self, listener):
		self.listeners.append(listener)

	def post(self, dataChunk):
		""" asynch broadcast """
		for l in self.listeners:
			AnonymousThread(func_notif(l,dataChunk)).start()

class DataBuffer(object):
	"""docstring for DataBuffer
	   this buffer is filled until on data fits
	   then it's cleaned and starts from the top
	   it's thought to be used in to show the signals
	   """

	def __init__(self,nChannels,nSamples,subsampling=1,callback=None):
		super(DataBuffer, self).__init__()
		self.chans=nChannels
		self.logger=logging.getLogger("logger")
		self.nSamples=nSamples
		self.chans=nChannels
		self.subsampling=subsampling
		self.lock=threading.Lock()
		self.buffpos=0
		self.callback=callback
		self.buff=np.zeros((self.nSamples,self.chans))


	def reset(self):
		self.buff=np.zeros((self.nSamples,self.chans))
		self.buffpos=0

	def notify(self,dataChunk):
		self.lock.acquire()
		mat=dataChunk.matrix[::self.subsampling,:]

		if mat.shape[0]>self.buff.shape[0]-self.buffpos:
                        AnonymousThread(func_callback(self.callback,np.copy(self.buff))).start()
			self.reset()
		#copy new data to buf
		self.buff[self.buffpos:self.buffpos+mat.shape[0],:]=mat
		self.buffpos+=mat.shape[0]
		self.lock.release()

	def getBuff(self):
		self.lock.acquire()
		cp=np.copy(self.buff)
		self.lock.release()
		return cp

class DataChunk(object):
	"""docstring for DataChunk"""
	def __init__(self, chans,samples,matrix):
		super(DataChunk, self).__init__()
		self.chans = chans
		self.samples = samples
		self.matrix=matrix

def func_notif(listener,data):
	return lambda: listener.notify(data)

def func_callback(fun,data):
	return lambda: fun(data)

class AnonymousThread(threading.Thread):
	"""docstring for AnonymousThread"""
	def __init__(self, function):
		super(AnonymousThread, self).__init__()
		self.function= function
	def run(self):
		self.function()
