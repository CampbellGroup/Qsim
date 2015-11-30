from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui

class PumpClient(QtGui.QWidget):
    
    def __init__(self, reactor, parent = None):
        super(PumpClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor         
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to pumpserver and
        connects incoming signals to relavent functions
        
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name = "Pump client")
        self.server = yield self.cxn.laserquantumpumpserver 
        self.initializeGUI()
       
    def initializeGUI(self):  
        layout = QtGui.QGridLayout() 
        label = QtGui.QLabel('empty label')   
	progbar = QtGui.QProgressBar()
	progbar.setGeometry(30, 40, 200, 25)
	progbar.setValue(12.0)
        layout.addWidget(label, 0,0)
        layout.addWidget(progbar, 0,0)
        self.setLayout(layout)
        from twisted.internet.reactor import callLater
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    PumpWidget = PumpClient(reactor)
    PumpWidget.show()
    reactor.run()
        
