from pymatlab.matlab import MatlabSession
import datetime
import logging
import threading
import data.bus as bus
import globals

class BCIConn(object):
    """Connects wit matlab to process the signals and classification"""

    MATLAB_STR="matlab -nojvm -nodisplay "
    INIT="brainz=Brainz(user,session);brainz.init();"
    START_TRIAL="brainz.startTrial()"
    ADD_DATA="c=brainz.addData(data)"
    END_TRIAL="brainz.endTrial()"


    def __init__(self,user,session):
        """@todo: to be defined """
        self.session=None
        self.logger=logging.getLogger("logger")
        self.user=user
        self.sessionId=session
        self.lock=threading.Lock()
        self.onTrial=False

    def start(self):
        """ inits the session with matlab
        """
        self.logger.debug("Starting matlab session %s",BCIConn.MATLAB_STR)
        self.session = MatlabSession(BCIConn.MATLAB_STR)
        self.logger.info("Matlab session started")
        self.session.putvalue('user',self.user)
        self.session.putvalue('session',self.sessionId)
        self.session.run(BCIConn.INIT)
        self.logger.debug("Matlab brainz object init with user %i and session %i",self.user,self.sessionId)

    def close(self  ):
        """Closes the matlab session
        """
        self.session.close()
        self.logger.info("Matlab session closed")

    def startTrial(self):
        """Sends the start trial signal to the matlab object
        """
        
        self.lock.acquire();
        self.logger.debug("Sending new trial")
        res=self.session.run(BCIConn.START_TRIAL)
        self.onTrial=True
	if res!=None:
        	self.logger.error("Matlab complained %s"%res)

        self.lock.release();

    def endTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.onTrial=False
        self.lock.acquire();
        self.logger.debug("Finish trial")
        res=self.session.run(BCIConn.END_TRIAL)
	if res!=None:
        	self.logger.error("Matlab complained %s"%res)
        self.lock.release();

    def append(self, data):
        """sends a matrix of data to matlab to process it
        :data: 2-D matrix with the data
        :class: the output of the clasification or nil
        """
        if not self.onTrial:
                return -1
        self.lock.acquire();
	#self.logger.debug("Sending data to matlab")
        self.session.putvalue('data',data)
        res=self.session.run(BCIConn.ADD_DATA)
	if res!=None:
        	self.logger.error("Matlab complained %s"%res)

        c=self.session.getvalue('c')
	self.logger.debug("Data classified as %i",c)
        self.lock.release();
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
            c=self.bciConn.append(mat)
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
