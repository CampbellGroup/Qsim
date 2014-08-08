from common.lib.clients.qtui.switch import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui

class cameraswitch(QtGui.QWidget):
    
    def __init__(self, reactor, parent = None):
        super(cameraswitch, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor         
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions
        
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name = "camera switch client")
        self.server = yield self.cxn.arduinottl  
        self.reg = yield self.cxn.registry 
        
        try:
            yield self.reg.cd('settings')
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except:
            self.settings = [] 
        self.initializeGUI()
    
    @inlineCallbacks    
    def initializeGUI(self):  
        layout = QtGui.QGridLayout()
        widget = QCustomSwitchChannel('Camera/PMT Toggle', ('PMT', 'Camera'))
        if 'cameraswitch' in self.settings:
            value = yield self.reg.get('cameraswitch')
            widget.TTLswitch.setChecked(value)
        else:
            widget.TTLswitch.setChecked(False)
            
        widget.TTLswitch.toggled.connect(self.toggle) 
        layout.addWidget(widget)
        self.setLayout(layout)
        
    @inlineCallbacks
    def toggle(self, state):
        yield self.server.ttl_output(8, True)
        yield self.server.ttl_output(8, False)
        if 'cameraswitch' in self.settings:
            yield self.reg.set('cameraswitch', state)
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    cameraswitchWidget = cameraswitch(reactor)
    cameraswitchWidget.show()
    reactor.run()
        