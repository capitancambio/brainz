import unittest
from data.writer import DataPath
import data.writer 
import numpy as np
import scipy.io as sio
import os
class DataWriterTest(unittest.TestCase):
	"""docstring for DataWriterTest"""
	def __init__(self, name):
		super(DataWriterTest, self).__init__(name)
		self.name = name
				
	def setUp(self):
		self.dPath=DataPath('/tmp/dx.mat','/tmp/dy.mat')

	def tearDown(self):
		try:
			os.remove(self.dPath.data) 
		except Exception,e:
			print e	
		try:
			os.remove(self.dPath.label) 
		except Exception,e:
			print e	

	def testHelperFirstWrite(self):
		trial=np.array([[1,2,3],[4,5,6]])	
		data.writer.matlab_data_helper_append(self.dPath,trial,1)
		mData=sio.loadmat(self.dPath.data)
		mLab=sio.loadmat(self.dPath.label)
		x =mData['x']
		y =mLab['y']
		self.assertTrue((x[:,:,0]==trial).all())
		self.assertTrue((y==[1]).all())

	def testHelperSeqWrite(self):
		trial=np.array([[1,2,3],[4,5,6]])	
		data.writer.matlab_data_helper_append(self.dPath,trial,1)
		trial2=np.copy(trial)*2
		trial3=np.copy(trial)*3
		data.writer.matlab_data_helper_append(self.dPath,trial2,2)
		data.writer.matlab_data_helper_append(self.dPath,trial3,1)
		mData=sio.loadmat(self.dPath.data)
		mLab=sio.loadmat(self.dPath.label)
		x =mData['x']
		y =mLab['y']
		self.assertTrue((x[:,:,0]==trial).all())
		self.assertTrue((x[:,:,1]==trial2).all())
		self.assertTrue((x[:,:,2]==trial3).all())
		self.assertTrue((y==[1,2,1]).all())
