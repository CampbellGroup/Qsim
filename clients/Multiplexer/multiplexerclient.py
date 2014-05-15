from clients.qtui.multiplexerchannel import QCustomWavemeterChannel
from twisted.internet.defer import inlineCallbacks, returnValue
from clients.connection import connection
from PyQt4 import QtGui
from wlm_client_config import multiplexer_config

    
SIGNALID1 = 445566
    
class wavemeterchannel(QtGui.QWidget):

    def __init__(self, reactor, parent = None):
        super(wavemeterchannel, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor     
        self.d = {} 
        self.chaninfo = multiplexer_config.info     
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('169.232.156.230')
        self.server = yield self.cxn.multiplexerserver
        yield self.server.signal__frequency_changed(SIGNALID1)
        yield self.server.addListener(listener = self.updateFrequency, source = None, ID = SIGNALID1) 
        self.initializeGUI()
        
    @inlineCallbacks
    def initializeGUI(self):  
        
        layout = QtGui.QGridLayout()
        for chan in self.chaninfo:
            port = self.chaninfo[chan][0]
            freq = self.chaninfo[chan][1]
            widget = QCustomWavemeterChannel(chan, freq) 
            import RGBconverter as RGB  
            RGB = RGB.RGBconverter()
            color = int(2.998e8/(float(freq)*1e3))
            color = RGB.wav2RGB(color)
            color = tuple(color)
            widget.currentfrequency.setStyleSheet('color: rgb' + str(color))
            widget.spinExp.valueChanged.connect(lambda exp = widget.spinExp.value(), port = port : self.expChanged(exp, port))
            initvalue = yield self.server.get_exposure(port)
            widget.spinExp.setValue(initvalue)
            widget.spinFreq.valueChanged.connect(self.freqChanged)
            self.d[port] = widget
            layout.addWidget(self.d[port])
        self.setLayout(layout)
        yield None

    
    @inlineCallbacks
    def expChanged(self, exp, chan):
        exp = int(exp)       
        yield self.server.set_exposure_time(chan,exp)
    
    def updateFrequency(self , c , signal):        
        chan = signal[0]
        freq = signal[1]
        self.d[chan].currentfrequency.setText(str(freq)[0:10])

    def freqChanged(self,value ):
        print value

    def closeEvent(self, x):
        self.reactor.stop()
        
        
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    wavemeterWidget = wavemeterchannel(reactor)
    wavemeterWidget.show()
    reactor.run()
    