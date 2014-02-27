#!/usr/bin/env python
import logging
import yaml
import os
import sys
import plotting.data_plotter
from conn.biosemi import BiosemiClient, DataPoster, DataBuilder
from data.bus import DataBus, DataBuffer
from data.writer import DataWriter, DataPath, DataAppender
from acqui.launcher import AcquiLauncher


logger = logging.getLogger("logger")
hand = logging.StreamHandler()
hand2 = logging.FileHandler("log.txt", mode='a', encoding=None, delay=False)
logger.setLevel(logging.DEBUG)
hand.setLevel(logging.DEBUG)
hand2.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(name)s] - %(levelname)s - %(message)s")
hand.setFormatter(formatter)
hand2.setFormatter(formatter)
logger.addHandler(hand)
logger.addHandler(hand2)


if len(sys.argv) != 2:
	print "REMEMBER THE USER!!"
	raise RuntimeError
user = sys.argv[1]
path = "cnf.yml"
logger.debug("Loading config from %s"%path)
cnf = yaml.load(file(path,"r"))
trialDur = (cnf['durations']['fixation']+cnf['durations']['class'])/1000*cnf['fs']
dataBuilder = DataBuilder(cnf['tcpLen'],cnf['channels'], cnf['samples'])
bioConn = BiosemiClient(cnf['host'],cnf['port'],dataBuilder)
bioConn.init()
#buffering stuff
dBus = DataBus()
dPoster = DataPoster(dBus,bioConn)
#we dont want to accumulate things in the tcp buff
dPoster.start()
logger.debug("After running poster")
#buffer
dBuff = DataBuffer(cnf['channels'],cnf['fs']*8,subsampling = 1)
dBus.register(dBuff)
path = DataPath(cnf['outputpath']+os.sep+user,'dx%s.mat','dy%s.mat')
path.clear()
logger.info('trial duration set to %i'%trialDur)
dataAppender = DataAppender(path,trialDur)
dataWriter = DataWriter(dataAppender)
dBus.register(dataWriter)
#gui
plotter = plotting.data_plotter.DataPlotter(dBuff)
#do magic
plotter.start()
l = AcquiLauncher(cnf,dataWriter)
l.start()
plotter.join()
#stop
l.join()
dPoster.stop()
dPoster.join()
bioConn.close()
