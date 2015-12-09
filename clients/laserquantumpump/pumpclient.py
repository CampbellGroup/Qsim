from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui, QtCore

SIGNALID1 = 441956
SIGNALID2 = 446296

class PumpClient(QtGui.QWidget):
    
    def __init__(self, reactor, cxn = None):
        super(PumpClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
	self.cxn = cxn
        self.reactor = reactor         
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to pumpserver and
        connects incoming signals to relavent functions
        
        """
        from labrad.wrappers import connectAsync
	if self.cxn is None:
            self.cxn = connection(name='Pump Client')
            yield self.cxn.connect()
	self.server = yield self.cxn.get_server('laserquantumpumpserver')
        #self.server = yield self.cxn.laserquantumpumpserver 

        yield self.server.signal__current_changed(SIGNALID1)
        yield self.server.signal__power_changed(SIGNALID2)

        yield self.server.addListener(listener = self.updateCurrent, source = None, ID = SIGNALID1)
        yield self.server.addListener(listener = self.updatePower, source = None, ID = SIGNALID2)

        self.initializeGUI()
       
    def initializeGUI(self):  
        layout = QtGui.QGridLayout() 
	font = QtGui.QFont()
	font.setBold(True)
	font.setPointSize(30)
	self.title = QtGui.QLabel('Laser Quantum Pump Laser')
	self.title.setFont(font)
	self.title.setAlignment(QtCore.Qt.AlignCenter)
	self.currentlabel = QtGui.QLabel('Current')
	self.powerlabel = QtGui.QLabel('Power')

	self.currentprogbar = QtGui.QProgressBar()
	self.currentprogbar.setGeometry(30, 40, 200, 25)

	self.powerprogbar = QtGui.QProgressBar()
	self.powerprogbar.setGeometry(30, 40, 200, 25)
	self.powerprogbar.setMaximum(100)
	self.powerprogbar.setMinimum(0)

	layout.addWidget(self.title,0,0)
        layout.addWidget(self.currentprogbar, 2,0)
        layout.addWidget(self.powerprogbar, 4,0)
        layout.addWidget(self.currentlabel, 1,0)
        layout.addWidget(self.powerlabel, 3,0)


        self.setLayout(layout)
        from twisted.internet.reactor import callLater

    def updateCurrent(self,c,  current):
	self.currentprogbar.setValue(current)

    def updatePower(self, c, power):
	powerperc = power['W']*100/8.0
	self.powerprogbar.setValue(powerperc)
	self.powerprogbar.setFormat(str(power['W']) + 'W')
	#self.powerprogbar.setFormat('23')


    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    PumpWidget = PumpClient(reactor)
    PumpWidget.show()
    reactor.run()
        
