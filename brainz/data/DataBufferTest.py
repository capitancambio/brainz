import unittest
from data.bus import DataBuffer,DataChunk
import numpy as np
class DataBufferTest(unittest.TestCase):
	"""unit tests"""
	def __init__(self, name):
		super(DataBufferTest, self).__init__(name)
		self.name = name
		
	def setUp(self):
		self.step1=np.array([[ 1.,  2.],
			[ 1., 2.],
			[ 1., 2.],
			[ 0., 0.],
			[ 0., 0.],
			[ 0., 0.],
			[ 0., 0.],
			[ 0., 0.],
			[ 0., 0.]])

		self.step2=np.array([
			[ 1., 2.],
			[ 1., 2.],
			[ 1., 2.],
			[ 3., 4.],
			[ 3., 4.],
			[ 3., 4.],
			[ 0., 0.],
			[ 0., 0.],
			[ 0., 0.]])
		self.step3=np.array([
			[ 1., 2.],
			[ 1., 2.],
			[ 1., 2.],
			[ 3., 4.],
			[ 3., 4.],
			[ 3., 4.],
			[ 5., 6.],
			[ 5., 6.],
			[ 5., 6.],
			])

		
	def testNotify(self):
		db=DataBuffer(2,9,1)
		mat=np.array([[1,1,1],[2,2,2]]).transpose()
		chunk=DataChunk(mat.shape[1],mat.shape[0],mat)
		db.notify(chunk)
		self.assertTrue((db.getBuff()==self.step1).all())
		#step 2
		mat=np.array([[3,3,3],[4,4,4]]).transpose()
		chunk=DataChunk(mat.shape[1],mat.shape[0],mat)
		db.notify(chunk)
		self.assertTrue((db.getBuff()==self.step2).all())
		#step 3
		mat=np.array([[5,5,5],[6,6,6]]).transpose()
		chunk=DataChunk(mat.shape[1],mat.shape[0],mat)
		db.notify(chunk)
		self.assertTrue((db.getBuff()==self.step3).all())
		#step 4 must be equal to step 1
		mat=np.array([[1,1,1],[2,2,2]]).transpose()
		chunk=DataChunk(mat.shape[1],mat.shape[0],mat)
		db.notify(chunk)
		self.assertTrue((db.getBuff()==self.step1).all())




