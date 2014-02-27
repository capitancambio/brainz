import logging
import datetime
import numpy as np
import os
import scipy.io as sio
import threading
class DataWriter(object):
    """docstring for DataWriter"""
    IDLE=0
    GATHERING=1
    DONE=2
    def __init__(self,mDataAppender):
        super(DataWriter, self).__init__()
        self.dataAppender=mDataAppender
        self.label=-1
        self.state=DataWriter.IDLE
        self.logger=logging.getLogger("logger")
        self.stTime=0
        self.sem=threading.Lock()

    def notify(self,bus,data):
        self.sem.acquire()
        if self.state==DataWriter.GATHERING:
            self.dataAppender.append(data)
        elif self.state==DataWriter.DONE:
            self.state=DataWriter.IDLE
            self.dataAppender.append(data)
            self.dataAppender.store(self.label)
            t=datetime.datetime.now()-self.stTime
            t=t.seconds+t.microseconds/1000000.
            self.logger.debug("delta time %f"%t)

        self.sem.release()

    def startWriting(self,bus,clazz):
        self.logger.debug("Starting to gather data")
        self.state=DataWriter.GATHERING
        self.stTime=datetime.datetime.now()

    def stopWriting(self,bus,clazz):
        self.logger.debug("done and dumping data (class %i)"%clazz)
        self.label=clazz
        self.state=DataWriter.DONE

class DataPath(object):
	"""docstring for DataPath"""
	def __init__(self, basePath,data,label):
		super(DataPath, self).__init__()
		self.basePath=basePath

		inst=datetime.datetime.now()
		self._data=(self.basePath+os.sep+data)%inst.strftime('%Y%m%d%H%M%S')
		self._label =(self.basePath+os.sep+label)%inst.strftime('%Y%m%d%H%M%S')
		self.logger=logging.getLogger("logger")
		try:
			os.makedirs(self.basePath)
		except Exception:
			self.logger.debug("dir %s already exists..."%self.basePath)
	def clear(self):
		#try:
			#self.logger.debug("Clearing files")
			#os.remove(self._data)
			#os.remove(self._label)
		#except Exception :
			pass
	@apply
	def data():
		def fget(self):
			return self._data

		return property(**locals())
	@apply
	def label():
		def fget(self):
			return self._label

		return property(**locals())

class DataAppender(object):
	"""docstring for DataAppender"""
	def __init__(self,path,length):
		super(DataAppender, self).__init__()
		self.logger=logging.getLogger("logger")
		self.path=path
		self.buff=None
		self.length=length

	def append(self, dataChunk):
		if self.buff==None:
			self.buff=np.copy(dataChunk.matrix)
		else:
			self.buff=np.vstack((self.buff,dataChunk.matrix))
			#self.logger.debug("data %i",self.buff.shape[0])
	def store(self,label):
		if self.buff.shape[0]< self.length:
			self.logger.error("The length of the buffer is less than expected... %i %i"%(self.buff.shape[0],self.buff.shape[1]))
			self.buff=None
		else:
			self.logger.debug("in store")
                        print "data len %ix%i",(self.buff.shape[0],self.buff.shape[1])
			self.buff=self.buff[:self.length,:]
			#copy the buff so we wont have any buffer clashes
			AnonymousThread(appender_func(self.path,np.copy(self.buff),label)).start()
			self.buff=None

class AnonymousThread(threading.Thread):
	"""docstring for AnonymousThread"""
	def __init__(self, function):
		super(AnonymousThread, self).__init__()
		self.function= function
	def run(self):
		self.function()

def appender_func(path,buff,label):
	return lambda: matlab_data_helper_append(path,buff,label)


def matlab_data_helper_append(path,trial,label):
	#trial to segs,chans,trial number
	trial=np.transpose(np.array(trial,ndmin=3),axes=[1,2,0])
	label=np.array(label,ndmin=1)
	if  os.path.exists(path.data):
		fData= sio.loadmat(path.data)
		x=fData['x']
		#append the trial
		x=np.concatenate((x,trial),axis=2)
		logging.getLogger("logger").debug("writing trial #%i",x.shape[2])
		fLabels=sio.loadmat(path.label)
		#work around to avoid the strange behaviour with 1-D vectors
		y=fLabels['y'][0,:]
		y=np.concatenate((y,label))
	else:
		logging.getLogger("logger").debug("writing first trial")
		x=trial
		y=label
	sio.savemat(path.data,{'x':x})
	sio.savemat(path.label,{'y':y},oned_as='row')

