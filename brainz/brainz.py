#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import yaml
import os
import sys
import fake

from matlab import BCIConn, BCIConnDataBuffer
from conn.biosemi import BiosemiClient, DataPoster, DataBuilder
from data.bus import DataBus
from data.writer import DataWriter, DataPath, DataAppender
import launcher
import sequence_generator
import globals
# logging


logger = logging.getLogger('logger')
hand = logging.StreamHandler()
hand2 = logging.FileHandler('brainz.txt', mode='a', encoding=None, delay=False)
logger.setLevel(logging.DEBUG)
hand.setLevel(logging.DEBUG)
hand2.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(name)s] - %(levelname)s - %(message)s')
hand.setFormatter(formatter)
hand2.setFormatter(formatter)
logger.addHandler(hand)
logger.addHandler(hand2)


# globals

class SequenceBciConn(object):
        """Docstring for SequenceBciConn """

        def __init__(self,sequence):
                """@todo: to be defined

                :sequence: @todo

                """
                self._sequence = sequence
                self._count=-1
                self._trial=False
        
        def start(self):
                """@todo: Docstring for start
                :returns: @todo

                """
                pass

        def close(self):
                """@todo: Docstring for close
                :returns: @todo

                """
                pass

        def startTrial(self):
                """@todo: Docstring for startTrial
                :returns: @todo

                """
                self._count+=1
                self._trial=True

        def endTrial(self):
                """@todo: Docstring for endTrial
                :returns: @todo

                """
                self._trial=False

        def append(self,data):
                """@todo: Docstring for append
                :returns: @todo

                """
                c=-1
                if self._trial:
                        c=self._sequence[self._count]
                return c


def buildBiosemiConn(cnf, dataBuilder):
    """@todo: Docstring for buildBiosemiConn

    :arg1: @todo
    :returns: @todo

    """

    globals.FAKE_IT
    bioConn = None
    if not globals.FAKE_IT:
        bioConn = BiosemiClient(cnf['host'], cnf['port'], dataBuilder)
    else:
        bioConn = fake.FakeBioSemi(dataBuilder)
    return bioConn



def buildBCIConn(user, session):
    """@todo: Docstring for buildBiosemiConn

    :arg1: @todo
    :returns: @todo

    """

    bciConn = None
    if not globals.FAKE_IT:
        bciConn = BCIConn(int(user), int(session)-1)
    else:
        bciConn = fake.FakeBCIConn()
    return bciConn


if len(sys.argv) != 3:
    print 'REMEMBER THE USER AND SESSION!!'
    raise RuntimeError

user = sys.argv[1]
session = sys.argv[2]

# load conf

path = 'brainz.yml'
logger.debug('Loading config from %s' % path)
cnf = yaml.load(file(path, 'r'))
cnf['user']=user
cnf['session']=session

trialDur = (cnf['durations']['fixation'] + cnf['durations']['class']) / 1000 * cnf['fs']

logger.info('Initialising...')
logger.info('trial duration set to %i' % trialDur)

# bioSemi connection

dataBuilder = DataBuilder(cnf['tcpLen'], cnf['channels'], cnf['samples'])
bioConn = buildBiosemiConn(cnf, dataBuilder)
bioConn.init()

logger.info('BiosemiConn up')

##buffering stuff

dBus = DataBus()
dPoster = DataPoster(globals.BUS, bioConn)

##we dont want to accumulate things in the tcp buff

dPoster.start()

logger.info('DataPoster configured')

path = DataPath(cnf['outputpath'] + os.sep + user, 'dx%s.mat', 'dy%s.mat')
path.clear()

dataAppender = DataAppender(path, trialDur)
dataWriter = DataWriter(dataAppender)
globals.BUS.subscribe(DataPoster.DATA_EVENT, dataWriter.notify)
globals.BUS.subscribe(globals.TRIAL_START_EVENT, dataWriter.startWriting)
globals.BUS.subscribe(globals.TRIAL_STOP_EVENT, dataWriter.stopWriting)
logger.info('Data writer registered')
generator=None
bciConn=None
##connection with matlab
if int(session)<=2:
        sequence,err=sequence_generator.generate(int(cnf['game']['trials']))
        generator=launcher.TrainingTrialGenerator(sequence)
        bciConn=SequenceBciConn(sequence)
else:
        generator=launcher.TrialGenerator(int(cnf['game']['trials']))
        bciConn = buildBCIConn(int(user), int(session))

bciConn.start()
bciConnBuffer = BCIConnDataBuffer(bciConn, cnf['channels'], 64)  # more than 64 assures RT
globals.BUS.subscribe(DataPoster.DATA_EVENT, bciConnBuffer.notify)
globals.BUS.subscribe(globals.TRIAL_START_EVENT, bciConnBuffer.startTrial)
globals.BUS.subscribe(globals.TRIAL_STOP_EVENT, bciConnBuffer.stopTrial)
logger.info('BCI conn registered')
# test
#cosa=fake.TrialTicker()
#cosa.start()

#import time
#time.sleep(40)
##appending and writing data

##init Brainz!
brainz=None
brainz = launcher.BrainzLauncher(cnf,generator)

brainz.run()
logger.info("done running...")
dPoster.stop()
dPoster.join()

# bioConn.close()
# bciConn.close()
# dPoster.stop()
# dPoster.join()

