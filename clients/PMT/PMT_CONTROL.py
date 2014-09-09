from PyQt4 import QtGui, uic
from twisted.internet.defer import inlineCallbacks
import os

SIGNALID = 874193

class pmtWidget(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(pmtWidget, self).__init__(parent)
        self.reactor = reactor
        basepath =  os.path.dirname(__file__)
        path = os.path.join(basepath, "pmtfrontend.ui")
        uic.loadUi(path,self)
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad import types as T
        self.T = T
        cxn = yield connectAsync()
        try:
            #connect to data vault and navigate to the directory boolean True to plot live
            self.server = yield cxn.arduino_counter   
        except AttributeError:
            self.server = None
            print 'Not Connected: Arduino ServerTypeError: unsupported operand ty' 
        yield self.setupListeners()
        #connect functions
        self.pushButton.setText('Off')
        self.pushButton.toggled.connect(self.on_toggled)
        self.newSet.clicked.connect(self.onNewSet)
        self.doubleSpinBox.valueChanged.connect(self.onNewDuration)
#        self.comboBox.currentIndexChanged.connect(self.onNewMode)
    
    @inlineCallbacks
    def setupListeners(self):
         yield self.server.signal__new_count(SIGNALID)
         yield self.server.addListener(listener = self.followSignal, source = None, ID = SIGNALID)
    def followSignal(self,signal,value):
        self.lcdNumber.display(value)
        
    @inlineCallbacks    
    def onNewSet(self,dummy):
        newset = yield self.server.new_data_set()
        self.lineEdit.setText(newset)
        
    @inlineCallbacks
    def on_toggled(self,value):
        if value:
            self.pushButton.setText('I')
        else: 
            self.pushButton.setText('O')
        yield self.server.toggle_counting(value)

    @inlineCallbacks
    def onNewDuration(self, value):
        yield self.server.set_update_time(self.T.Value(value, 's'))
    
    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    pmtWidget = pmtWidget(reactor)
    pmtWidget.show()
    reactor.run()
