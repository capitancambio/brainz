#!/usr/bin/env python
import unittest
import data.DataBufferTest
import data.DataWriterTest
suiteList=[
 unittest.TestLoader().loadTestsFromTestCase(data.DataBufferTest.DataBufferTest),
 unittest.TestLoader().loadTestsFromTestCase(data.DataWriterTest.DataWriterTest),
 ]
suite=unittest.TestSuite(suiteList)
unittest.TextTestRunner(verbosity=2).run(suite)
