import socket
import threading
import numpy as np
import logging
from data.bus import DataChunk

""" Client for biosemi """
class BiosemiClient(object):
	"""docstring for BioClient"""
	def __init__(self, host,port,dataBuilder):
		self.host=host
		self.port=port
		self.socket=None
		self.dataBuilder=dataBuilder
		self.logger=logging.getLogger("logger")
		self.isOpen=False

	def init(self):
		self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.logger.info("Connecting to %s:%i"%(self.host,self.port))
		self.socket.connect((self.host,self.port))
		self.logger.info("Connected")
		self.isOpen=True
	def close(self):
		self.socket.close()
		self.isOpen=False
		self.logger.info("Connection to %s:%i closed"%(self.host,self.port))

	def read(self,lengh):
		msg=''
		while len(msg)<lengh and self.isOpen:
			rdata=self.socket.recv(lengh-len(msg))
			if rdata=='':
				raise RuntimeError("Socket closed")
			msg+=rdata
		return msg
	def getChunk(self):
		return self.dataBuilder.build(self.read(self.dataBuilder.getArrayLen()))


class DataPoster(threading.Thread):
 	"""docstring for DataPoster"""
 	def __init__(self, eventBus,cli):
 		super(DataPoster, self).__init__()
 		self.eventBus = eventBus
		self.cli=cli
		self.logger=logging.getLogger("logger")
		self.running=0

	def run(self):
		self.logger.info("Poster initialised")
		self.running=1
		while self.running:
			self.eventBus.post(self.cli.getChunk())
		self.logger.info("Poster stopping")
	def stop(self):
		self.running=0

class DataBuilder(object):
	"""Gets the data from the client and
	process it to get a samplesxchannels ready to append matrix"""
	def __init__(self, arrayLen, nChannels, samplesPerChan):
		super(DataBuilder, self).__init__()
		self.arrayLen = arrayLen
		self.nChannels = nChannels
		self.samplesPerChan = samplesPerChan
		self.logger=logging.getLogger("logger")

	def getArrayLen(self):
		return self.arrayLen;

	def build(self, array):
		array=self.bit2float(array)

		array=np.reshape(array,(self.samplesPerChan,self.nChannels))
		return DataChunk(self.nChannels,array.shape[0],array)

	def bit2float(self, array):
		""" every sample is composed by 3 little endian bytes
		which means least sig 0 .. 8 9 .. 16 17 ..24 most significant ( sign )
		"""
		d0 = np.frombuffer(array[0::3], dtype='u1').astype(float)
		d1 = np.frombuffer(array[1::3], dtype='u1').astype(float)
		d2 = np.frombuffer(array[2::3], dtype='i1').astype(float)
		d0 += 256 * d1
		d0 += 65536 * d2
		d0 *= 31.25e-4 #to minivolts
		return	d0
