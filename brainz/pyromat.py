from pymatlab.matlab import MatlabSession
import time
import datetime
import logging
import numpy
import threading
import Pyro4

#logger = logging.getLogger('logger')
#hand = logging.StreamHandler()
#hand2 = logging.FileHandler('pyromat.txt', mode='a', encoding=None, delay=False)
#logger.setLevel(logging.DEBUG)
#hand.setLevel(logging.DEBUG)
#hand2.setLevel(logging.DEBUG)

#formatter = logging.Formatter('[%(name)s] - %(levelname)s - %(message)s')
#hand.setFormatter(formatter)
#hand2.setFormatter(formatter)
#logger.addHandler(hand)
#logger.addHandler(hand2)


class BCIConn(object):
    """Connects wit matlab to process the signals and classification"""

    MATLAB_STR="matlab -nojvm -nodisplay -logfile ~/tmp/logmat.txt"
    INIT="brainz=Brainz(user,session);brainz.init();"
    START_TRIAL="brainz.startTrial()"
    ADD_DATA="c=brainz.addData(data)"
    END_TRIAL="brainz.endTrial()"


    def __init__(self):
        """@todo: to be defined """
        self.logger=logging.getLogger("logger")
        self.session=None
        self.lock=threading.Lock()
        self.onTrial=False

    def start(self,user,session):
        """ inits the session with matlab
        """
        self.user=user
        self.sessionId=session
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
#        print "MATLAB %s"%threading.currentThread()
        if not self.onTrial:
                return -1
        #self.lock.acquire();
	self.logger.debug("Sending data to matlab")
        time1=time.time()
        data=numpy.array(data,dtype=numpy.float64)
        self.session.putvalue('data',data)
        res=self.session.run(BCIConn.ADD_DATA)
        if res!=None:
                self.logger.error("Matlab complained %s"%res)

        c=self.session.getvalue('c')

        ##time.sleep(1)
        time2=time.time()
	#self.logger.debug("Data classified as %i",c)
        #self.lock.release();
        return int(c)


daemon=Pyro4.Daemon()                 # make a Pyro daemon
ns=Pyro4.locateNS()                   # find the name server
uri=daemon.register(BCIConn())   # register the greeting object as a Pyro object
print uri
ns.register("bci.conn", uri)  # register the object with a name in the name server
daemon.requestLoop()
