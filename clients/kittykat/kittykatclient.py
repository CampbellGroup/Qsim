from common.lib.clients.qtui.switch import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui

class kittykatclient(QtGui.QWidget):
    
    def __init__(self, reactor, parent = None):
        super(kittykatclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor         
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions
        
        """
        from labrad.wrappers import connectAsync
        self.kittykat = False
        self.oldstate = False
        self.delay = 0.5
        self.cxn = yield connectAsync(name = "kitty kat client")
        self.server = yield self.cxn.arduinottl  
        self.reg = yield self.cxn.registry 
        self.initializeGUI()
    
    @inlineCallbacks    
    def initializeGUI(self):  
        layout = QtGui.QGridLayout()
        widget = QCustomSwitchChannel('Kitty Kat')       
        widget.TTLswitch.toggled.connect(self.toggle) 
        layout.addWidget(widget)
        self.setLayout(layout)
        from twisted.internet.reactor import callLater
        yield self.kittyloop()
        
    def toggle(self, state):
        '''
        Sets kitty kat on or off
        '''
        
        self.kittykat = state
#         yield self.server.ttl_output(8, True)
#         yield self.server.ttl_output(8, False)
#         yield self.server.ttl_read(8)#releases channel so manual control of cameraswitch is possible
#         if 'cameraswitch' in self.settings:
#             yield self.reg.set('cameraswitch', state)

    @inlineCallbacks
    def kittyloop(self):
        if self.kittykat:
            newstate = not self.oldstate
            yield self.server.ttl_output(10, newstate)
            self.oldstate = newstate
            reactor.callLater(self.delay, self.kittyloop)
        else:
            reactor.callLater(self.delay, self.kittyloop)
            
        
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
        