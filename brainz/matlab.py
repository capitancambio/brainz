from pymatlab.matlab import MatlabSession
from multiprocessing import Process 
import time
import datetime
import logging
import threading
import data.bus as bus
import numpy
import Pyro4
import globals

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')


class BCIProxy(object):
    """Connects wit matlab to process the signals and classification"""


    def __init__(self,user,session):
        """@todo: to be defined """
        self.bciConn=None
        self.logger=logging.getLogger("logger")
        self.user=user
        self.sessionId=session

    def start(self):
        nsproxy = Pyro4.naming.locateNS()
        self.bciConn=Pyro4.Proxy("PYRONAME:bci.conn")
        print self.bciConn
        self.bciConn.start(self.user,self.sessionId)

    def close(self):
            self.logger.debug("closing matlab proxy")
            self.bciConn.close()

    def startTrial(self):
            self.logger.debug("starting trial")
            self.bciConn.startTrial()

    def endTrial(self):
        self.logger.debug("ending trial")
        self.bciConn.endTrial()

    def append(self, data):
        self.logger.debug("sending data")
        time1=time.time()
        c=self.bciConn.append(data)

        time2=time.time()
        print "Pyro took: %f"%(time2-time1)
        return c
    


class BCIConnDataBuffer(object):
    """docstring for BCIConnDataBuffer"""
    IDLE=0
    GATHERING=1
    DONE=2
    def __init__(self,bciConn,nChan,nSamp):
        super(BCIConnDataBuffer, self).__init__()
        self.state=BCIConnDataBuffer.IDLE
        self.logger=logging.getLogger("logger")
        self.bciConn=bciConn
	self.buff=bus.DataBuffer(nChan,nSamp,callback=self.retrieve);
        self.stTime=0

    def notify(self,bus,data):
        if self.state==BCIConnDataBuffer.GATHERING:
            self.buff.notify(data)
        elif self.state==BCIConnDataBuffer.DONE:
            self.state=BCIConnDataBuffer.IDLE
            self.buff.notify(data)

            #TODO: this is the expected, so we can pass them together?
            #self.dataAppender.store(self.label)
            t=datetime.datetime.now()-self.stTime
            t=t.seconds+t.microseconds/1000000.
            self.logger.debug("matlab delta time %f"%t)

    def retrieve(self,mat):
            c=self.bciConn.append(mat.tolist())
            self.logger.debug("mat data buf emitting class %i"%c)
            globals.BUS.publish(globals.CLASS_EVENT,c)
	    

    def startTrial(self,bus,clazz):
        self.logger.debug("MATLAB startTrial(class %i)"%clazz)
        self.state=BCIConnDataBuffer.GATHERING
        self.stTime=datetime.datetime.now()
        self.bciConn.startTrial()
	self.buff.reset()

    def stopTrial(self,bus,clazz):
        self.logger.debug("MATLAB stopTrial(class %i)"%clazz)
        self.bciConn.endTrial()
        self.state=BCIConnDataBuffer.DONE

if __name__=="__main__":
       proxy= BCIProxy(201,1)
       proxy.start()
       proxy.startTrial()
       proxy.append([])
       proxy.endTrial()
       proxy.close()

