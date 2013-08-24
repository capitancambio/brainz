#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import logging
import threading
import random
import globals


class FakeBioSemi(object):

    def __init__(self, dataBuilder):
        """@todo: Docstring for __init__
        :returns: @todo

        """

        self.dataBuilder = dataBuilder

    def init(self):
        pass

    def getChunk(self):
        time.sleep(0.005)
        return self.dataBuilder.build('a' * self.dataBuilder.getArrayLen())


class FakeBCIConn(object):

    def __init__(self):
        """@todo: Docstring for __init__
        :returns: @todo

        """

        self.counter = 0
        self.logger = logging.getLogger('logger')
        self.lock = threading.Lock()

    def start(self):
        """Closes the matlab session
        """

        pass

    def close(self):
        """Closes the matlab session
        """

        pass

    def startTrial(self):
            pass

    def endTrial(self):
        self.logger.debug('processed %i samples' % self.counter)
        self.counter = 0

    def append(self, data):
        """sends a matrix of data to matlab to process it
        :data: 2-D matrix with the data
        :class: the output of the clasification or nil
        """
        self.lock.acquire()
        self.counter += data.shape[0]
        self.lock.release()
        return random.choice([1,2,3])


class TrialTicker(threading.Thread):

    """Docstring for TrialTicker """

    def __init__(self):
        """@todo: to be defined """

        threading.Thread.__init__(self)
        self.bus = globals.BUS
        self.setDaemon(True)
        self.logger = logging.getLogger('logger')

    def run(self):
        cl = 0
        while True:
            self.logger.debug('sending trial start %i', cl)
            self.bus.publish(globals.TRIAL_START_EVENT, cl)

            time.sleep(7)
            self.logger.debug('sending trial stop %i', cl)
            self.bus.publish(globals.TRIAL_STOP_EVENT, cl)
            time.sleep(1)
            cl = (cl + 1) % 3 + 1


