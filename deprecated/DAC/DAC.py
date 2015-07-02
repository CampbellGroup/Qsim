from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks
from config.DAC_client_config import DAC_config
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
        self.cxn2 = yield connectAsync(name = socket.gethostname() + " DAC client")
        self.reg = self.cxn2.registry
        yield self.reg.cd('settings')
        self.settings = yield self.reg.dir()
        self.settings = self.settings[1]
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
    
    @inlineCallbacks    
    def initializeGUI(self):  
        layout = QtGui.QGridLayout()
        
        qBox = QtGui.QGroupBox('Ez Voltages')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        for device in self.chaninfo:
            for i in range(2): 
                name = self.chaninfo[device][1][i]       
                position = self.chaninfo[device][i + 2]    
                widget = QCustomSpinBox(name + ' (V)', (-12.000, 12.000))
                if name in self.settings:
                    value = yield self.reg.get(name)
                    widget.spinLevel.setValue(value)
                widget.spinLevel.valueChanged.connect(lambda value = widget.spinLevel.value(), port = (device, i + 1)   : self.changeValue(value, port))         
                self.d[name] = widget
                subLayout.addWidget(self.d[name])
                
        self.setLayout(layout)
        
    @inlineCallbacks
    def changeValue(self, value, port):
        device = port[0]
        channel = port[1]
        name = self.chaninfo[device][1][channel - 1]
        ctx = self.chaninfo[device][4]
        from labrad.units import WithUnit
        value = WithUnit(value, 'V')

        yield self.server.apply_dc(channel, value, context = ctx)  
        yield self.reg.set(name, value)
    
    def closeEvent(self, x):
#        for device in self.chaninfo:
            ###TODO: release device not working
#            ctx = self.chaninfo[device][4]
#            yield self.server.release_device(context = ctx)
        self.reactor.stop()
                
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from Qsim.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DACWidget = DACclient(reactor)
    DACWidget.show()
    reactor.run()
    
    

        
        
