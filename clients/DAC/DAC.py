from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks
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
        self.server = yield self.cxn.rigol_dg1022a_server
        for device in self.chaninfo: #Iterate over config file
            dacctx = yield self.server.context() # grab contexts for N rigols
            deviceID = self.chaninfo[device][0] 
            self.chaninfo[device][4] = dacctx # stores context for later use
            yield self.server.select_device(deviceID, context = dacctx) #select device for given context
            for i in range(2):
                yield self.server.wave_function(i + 1, 'DC', context = dacctx)  #Sets Rigols to DC and Output on        
                yield self.server.output(i + 1, True, context = dacctx)
        self.initializeGUI()
        
    def initializeGUI(self):  
    
        layout = QtGui.QGridLayout()
        
        qBox = QtGui.QGroupBox('Rod Voltages')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        for device in self.chaninfo:
            for i in range(2): 
                name = self.chaninfo[device][1][i]       
                position = self.chaninfo[device][i + 2]    
                widget = QCustomSpinBox(name + ' (V)', (-5.000, 5.000))  
                widget.spinLevel.valueChanged.connect(lambda value = widget.spinLevel.value(), port = (device, i + 1)   : self.changeValue(value, port))         
                self.d[name] = widget
                subLayout.addWidget(self.d[name])
                
        self.setLayout(layout)
        
    @inlineCallbacks
    def changeValue(self, value, port):
        device = port[0]
        channel = port[1]
        from labrad.units import WithUnit
        value = WithUnit(value, 'V')
        ctx = self.chaninfo[device][4]
        yield self.server.apply_dc(channel, value, context = ctx)  

    def closeEvent(self, x):
        for device in self.chaninfo:
            ctx = self.chaninfo[device][4]
            self.server.release_device(context = ctx)
        self.reactor.stop()
                
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from Qsim.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DACWidget = DACclient(reactor)
    DACWidget.show()
    reactor.run()
    
    

        
        