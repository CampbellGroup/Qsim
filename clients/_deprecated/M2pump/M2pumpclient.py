from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui, QtCore

SIGNALID1 = 441956
SIGNALID2 = 446296
SIGNALID3 = 124462

class M2PumpClient(QtGui.QWidget):
    
    def __init__(self, reactor, cxn = None):
        super(M2PumpClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.cxn = cxn
        self.reactor = reactor         
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to pumpserver andLaser_Quantum_
        connects incoming signals to relavent functions
        
        """
        if self.cxn is None:
            self.cxn = connection(name='M2 Pump Client')
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('M2Pump')

        yield self.server.signal__current_changed(SIGNALID1)
        yield self.server.signal__power_changed(SIGNALID2)
        yield self.server.signal__temp_changed(SIGNALID3)

        yield self.server.addListener(listener = self.updateCurrent, source = None, ID = SIGNALID1)
        yield self.server.addListener(listener = self.updatePower, source = None, ID = SIGNALID2)
        yield self.server.addListener(listener = self.updateTemp,  source = None, ID = SIGNALID3)

        self.initializeGUI()
       
    def initializeGUI(self):  
        layout = QtGui.QGridLayout() 
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(18)
        self.title = QtGui.QLabel('M2 Pump Laser')
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        #self.setGeometry(20,30,100,500)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.templabel = QtGui.QLabel('Laser Temp')
        self.currentlabel = QtGui.QLabel('Current')
        self.powerlabel = QtGui.QLabel('Power')
        
        self.tempdisplay = QtGui.QLCDNumber()
        self.tempdisplay.setDigitCount(6)

        self.currentprogbar = QtGui.QProgressBar()
        self.currentprogbar.setOrientation(QtCore.Qt.Vertical)

        self.powerprogbar = QtGui.QProgressBar()
        self.powerprogbar.setOrientation(QtCore.Qt.Vertical)
        self.powerprogbar.setGeometry(30, 40, 25, 200)
        self.powerprogbar.setMaximum(100)
        self.powerprogbar.setMinimum(0)

        layout.addWidget(self.title,          0,0,1,2)
        layout.addWidget(self.currentprogbar, 2,0,8,1)
        layout.addWidget(self.powerprogbar,   2,1,8,1)
        layout.addWidget(self.currentlabel,   1,0,1,1)
        layout.addWidget(self.powerlabel,     1,1,1,1)
        layout.addWidget(self.templabel,      10,0,1,1)
        layout.addWidget(self.tempdisplay,    10,1,1,1)

        self.setLayout(layout)

    def updateCurrent(self,c,  current):
        self.currentprogbar.setValue(current['A'])

    def updatePower(self, c, power):
        powerperc = power['W']*100/8.0
        self.powerprogbar.setValue(powerperc)
        self.powerprogbar.setFormat(str(power['W']) + 'W')
        
    def updateTemp(self, c, temp):
        self.tempdisplay.display(str(temp['degC']))

    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    PumpWidget = M2PumpClient(reactor)
    PumpWidget.show()
    run = reactor.run()  # @UndefinedVariable
        
