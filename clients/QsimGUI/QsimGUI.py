from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks, returnValue
import sys

class QSIM_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, clipboard, parent=None):
        super(QSIM_GUI, self).__init__(parent)
        self.clipboard = clipboard
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.lib.clients.connection import connection
        cxn = connection(name = 'GUI Client')
        yield cxn.connect()
        self.create_layout(cxn)
    
    def create_layout(self, cxn):


        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout() 
        script_scanner = self.makeScriptControlWidget(reactor, cxn)
        control = self.makeControlWidget(reactor, cxn)
        from Qsim.clients.analysis.analysis import analysis
        
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(control, '&Control')
        self.tabWidget.addTab(script_scanner, '&Script Scanner')
        self.tabWidget.addTab(analysis(reactor, cxn), '&Analysis')
        self.createGrapherTab()
        
        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Qsim GUI')
   
   #THIS IS A HACK, DYLAN MAY FIX.....
   
        
    @inlineCallbacks
    def createGrapherTab(self):
        grapherTab = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapherTab, '&Grapher')
        
    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.lib.clients.pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def makeScriptControlWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        
        from common.lib.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        gridLayout = QtGui.QGridLayout()
      
        gridLayout.addWidget(script_scanner_gui(reactor))
        
        widget.setLayout(gridLayout)
        return widget
    
    def makeControlWidget(self, reactor, cxn):
        widget = QtGui.QWidget()

        from Qsim.clients.PMT.PMT_CONTROL import pmtWidget 
        from Qsim.clients.DAC.DAC import DACclient
        from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import switchclient
        from common.lib.clients.Multiplexer.multiplexerclient import wavemeterclient
        from common.lib.clients.pygrapherlive.grapherwindow import FirstWindow

#        grapherWindow = FirstWindow(None, cxn.context, reactor)
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(pmtWidget(reactor),                1,1, 1,1)
        gridLayout.addWidget(cameraswitch(reactor),             0,1, 1,1)
        gridLayout.addWidget(wavemeterclient(reactor),          0,0, 4,1)
        gridLayout.addWidget(switchclient(reactor),             2,1, 1,1)
        gridLayout.addWidget(DACclient(reactor),                3,1, 1,1)
 #       gridLayout.setVerticalSpacing(.01)
        widget.setLayout(gridLayout)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( sys.argv )
    clipboard = a.clipboard()
    import common.lib.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    QsimGUI = QSIM_GUI(reactor, clipboard)
    QsimGUI.setWindowIcon(QtGui.QIcon('/home/qsimexpcontrol/Pictures/icons/6ions.jpg'))
    QsimGUI.setWindowTitle('Qsim GUI')
    QsimGUI.show()
    reactor.run()
