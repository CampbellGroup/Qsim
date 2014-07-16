from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
from DAC_client_config import DAC_config
import socket

class DACclient(QtGui.QWidget):
    


    def __init__(self, reactor, parent = None):
        """initializels the GUI creates the reactor 
            and empty dictionary for channel widgets to 
            be stored for iteration. also grabs chan info
            from DAC_client_config file 
        """ 
        super(DACclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor     
        self.d = {} 
        self.chaninfo = DAC_config.info     
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter server to access DAC channels
        
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('10.97.112.2', name = socket.gethostname() + " DAC client")
        self.dac1 = yield self.cxn.rigol_dg1022_dac_1_server
        self.dac2 = yield self.cxn.rigol_dg1022_dac_2_server
        self.initializeGUI()
        
    @inlineCallbacks
    def initializeGUI(self):  
    
        layout = QtGui.QGridLayout()
        for chan in self.chaninfo:
            port = self.chaninfo[chan][0]
            position = self.chaninfo[chan][1]
            
            widget = QCustomSpinBox(chan, (-5.000, 5.000))  

            #connect things here
            widget.spinLevel.valueChanged.connect(lambda value = widget.spinLevel.value(), port = port   : self.changeValue(value, port))         
            self.d[port] = widget
            layout.addWidget(self.d[port])
        self.setLayout(layout)
        yield None
        
    @inlineCallbacks
    def changeValue(self, value, port):
        if port[0] == 1:
            yield self.dac1.apply_dc(port[1], value)
        else:
            yield self.dac2.apply_dc(port[1], value)

    def closeEvent(self, x):
        self.reactor.stop()
        
        
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DACWidget = DACclient(reactor)
    DACWidget.show()
    reactor.run()