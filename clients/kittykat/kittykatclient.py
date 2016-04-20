from common.lib.clients.qtui.switch import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
from common.lib.clients.connection import connection

class kittykatclient(QtGui.QWidget):
    
    def __init__(self, reactor, cxn = None):
        super(kittykatclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.cxn = cxn
        self.reactor = reactor         
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions
        
        """
        
        self.kittykat = False
        self.oldstate = False
        self.delay = 500 # in ms this is half the total period (1s delay)
        if self.cxn is None:
            self.cxn = connection(name = 'kitty kat')
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('arduinottl')  
        self.reg = yield self.cxn.get_server('registry') 
        self.initializeGUI()
       
    def initializeGUI(self):  
        layout = QtGui.QGridLayout()
        switchwidget = QCustomSwitchChannel('Kitty Kat')   
        delaywidget = QtGui.QSpinBox()
        delaywidget.setRange(100, 10000)
        delaywidget.setValue(1000)
        delaywidget.valueChanged.connect(self.delaychanged) 
        delaylabel = QtGui.QLabel('delay (ms)')   
        switchwidget.TTLswitch.toggled.connect(self.toggle) 
        layout.addWidget(delaylabel, 1,1)
        layout.addWidget(switchwidget, 0,0)
        layout.addWidget(delaywidget, 1,0)
        self.setLayout(layout)
        from twisted.internet.reactor import callLater
        self.kittyloop()
        
    def toggle(self, state):
        '''
        Sets kitty kat on or off
        '''
        
        self.kittykat = state
        
    def delaychanged(self, delay):
        '''
        Sets Delay Time
        '''
        
        self.delay = delay/2.0

    @inlineCallbacks
    def kittyloop(self):
        if self.kittykat:
            newstate = not self.oldstate
            yield self.server.ttl_output(10, newstate)
            self.oldstate = newstate
            self.reactor.callLater(self.delay /1000.0, self.kittyloop)
        else:
            self.reactor.callLater(self.delay / 1000.0, self.kittyloop)
            
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    kittykatWidget = kittykatclient(reactor)
    kittykatWidget.show()
    reactor.run()
        
