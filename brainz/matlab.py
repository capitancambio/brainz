from pymatlab.matlab import MatlabSession
import datetime
import logging
import threading

class BCIConn(object):
    """Connects wit matlab to process the signals and classification"""

    MATLAB_STR="matlab -nojvm -nodisplay"
    INIT="brainz=Brainz(user)"
    START_TRIAL="brainz.startTrial()"
    ADD_DATA="brainz.addData(data);clear data;"
    CLASSIFY="c=brainz.classify()"
    END_TRIAL="brainz.endTrial()"


    def __init__(self,user):
        """@todo: to be defined """
        self.session=None
        self.logger=logging.getLogger("logger")
        self.user=user
        self.lock=threading.Lock()

    def start(self):
        """ inits the session with matlab
        """
        self.logger.debug("Starting matlab session %s",BCIConn.MATLAB_STR)
        self.session = MatlabSession(BCIConn.MATLAB_STR)
        self.logger.info("Matlab session started")
        self.session.putvalue('user',self.user)
        self.run(BCIConn.INIT)
        self.logger.debug("Matlab brainz object init with user",self.user)

    def close(self  ):
        """Closes the matlab session
        """
        self.session.close()
        self.logger.info("Matlab session closed")

    def startTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.lock.aquire();
        self.logger.debug("Sending new trial")
        self.session.run(BCIConn.START_TRIAL)
        self.lock.release();

    def endTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.lock.aquire();
        self.logger.debug("Finish trial")
        self.session.run(BCIConn.END_TRIAL)
        self.lock.release();

    def append(self, data):
        """sends a matrix of data to matlab to process it
        :data: 2-D matrix with the data
        :class: the output of the clasification or nil
        """
        self.lock.aquire();
        self.logger.debug("Sending data to matlab")
        self.session.putvalue('data',data)
        self.session.run(BCIConn.ADD_DATA)
        self.session.run(BCIConn.CLASSIFY)
        c=self.session.getvalue('c')
        self.logger.debug("Data classified as %i",c)
        self.lock.release();
        return c


class BCIConnDataBuffer(object):
    """docstring for BCIConnDataBuffer"""
    IDLE=0
    GATHERING=1
    DONE=2
    def __init__(self,bciConn):
        super(BCIConnDataBuffer, self).__init__()
        self.state=BCIConnDataBuffer.IDLE
        self.logger=logging.getLogger("logger")
        self.bciConn=bciConn
        self.stTime=0

    def notify(self,bus,data):
        if self.state==BCIConnDataBuffer.GATHERING:
            self.bciConn.append(data)
        elif self.state==BCIConnDataBuffer.DONE:
            self.state=BCIConnDataBuffer.IDLE
            self.bciConn.append(data)

            #TODO: this is the expected, so we can pass them together?
            #self.dataAppender.store(self.label)
            #t=datetime.datetime.now()-self.stTime
            #t=t.seconds+t.microseconds/1000000.
            #self.logger.debug("matlab delta time %f"%t)

    def startTrial(self,bus,clazz):
        self.logger.debug("BCI startTrial(class %i)"%clazz)
        self.state=BCIConnDataBuffer.GATHERING
        self.bciConn.startTrial()
        self.stTime=datetime.datetime.now()

    def stopTrial(self,bus,clazz):
        self.logger.debug("BCI stopTrial(class %i)"%clazz)
        self.state=BCIConnDataBuffer.DONE
