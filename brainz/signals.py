from pymatlab.matlab import MatlabSession


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
        self.user

    def start(self):
        """ inits the session with matlab
        """
        self.session = MatlabSession(SignalProcessor.MATLAB_STR)
        self.session.putvalue('user',self.user)
        self.run(SignalProcessor.INIT)

    def close(self  ):
        """Closes the matlab session
        """
        self.session.close()

    def startTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.session.run(SignalProcessor.START_TRIAL)

    def endTrial(self):
        """Sends the start trial signal to the matlab object
        """
        self.session.run(SignalProcessor.END_TRIAL)

    def addData(self, data):
        """sends a matrix of data to matlab to process it
        :data: 2-D matrix with the data
        :class: the output of the clasification or nil
        """
        self.session.putvalue('data',data)
        self.session.run(SignalProcessor.ADD_DATA)
        self.session.run(SignalProcessor.CLASSIFY)
        c=self.session.getvalue('c')
        return c

