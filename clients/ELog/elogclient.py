from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui

class ELog(QtGui.QWidget):
    


    def __init__(self, reactor, parent = None):
        """initializels the GUI creates the loop (reactor) for twisted
        """ 
            
        super(Elog, self).__init__() # here we inherit all the init functions from QWidgets
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor        
        self.connect()
        