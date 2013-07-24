from pymatlab.matlab import MatlabSession
import logging

class SignalProcessor(object):
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

    def start(self):
        """ inits the session with matlab
        """
        self.logger.debug("Starting matlab session %s",SignalProcessor.MATLAB_STR)
        self.session = MatlabSession(SignalProcessor.MATLAB_STR)
        self.logger.info("Matlab session started")
        self.session.putvalue('user',self.user)
        self.run(SignalProcessor.INIT)
        self.logger.debug("Matlab brainz object init with user",self.user)

    def close(self  ):
        """Closes the matlab session
        """
        self.session.close()
        self.logger.info("Matlab session closed")

    def startTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.logger.debug("Sending new trial")
        self.session.run(SignalProcessor.START_TRIAL)

    def endTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.logger.debug("Finish trial")
        self.session.run(SignalProcessor.END_TRIAL)

    def addData(self, data):
        """sends a matrix of data to matlab to process it
        :data: 2-D matrix with the data
        :class: the output of the clasification or nil
        """
        self.logger.debug("Sending data to matlab")
        self.session.putvalue('data',data)
        self.session.run(SignalProcessor.ADD_DATA)
        self.session.run(SignalProcessor.CLASSIFY)
        c=self.session.getvalue('c')
        self.logger.debug("Data classified as %i",c)
        return c

