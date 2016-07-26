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
        cxn = connection(name = 'Qsim GUI Client')
        yield cxn.connect()
        self.create_layout(cxn)

    #Highest level adds tabs to big GUI
    def create_layout(self, cxn):
	    #creates central layout
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()

	    #create subwidgets to be added to tabs
        script_scanner = self.makeScriptScannerWidget(reactor, cxn)
        wavemeter = self.makeWavemeterWidget(reactor, cxn)
        #M2 = self.makeM2Widget(reactor, cxn)
        control = self.makeControlWidget(reactor, cxn)
        analysis = self.makeAnalysisWidget(reactor, cxn)
        Tsunami = self.makeTsunamiWidget(reactor, cxn)
	Pulser = self.makePulserWidget(reactor, cxn)

        # add tabs
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(wavemeter, '&Wavemeter')
        #self.tabWidget.addTab(M2, '&M2')
        self.tabWidget.addTab(script_scanner, '&Script Scanner')
        self.tabWidget.addTab(control, '&Control')
        self.tabWidget.addTab(analysis, '&Analysis')
        self.tabWidget.addTab(Tsunami, '&Tsunami')
	self.tabWidget.addTab(Pulser, '&Pulser')

        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Qsim GUI')

#################### Here we will connect to individual clients and add sub-tabs #####################

######sub tab layout example#############
#    def makeLaserSubTab(self, reactor, cxn):
#        centralWidget = QtGui.QWidget()
#        layout = QtGui.QHBoxLayout()

#	wavemeter = self.makeWavemeterWidget(reactor, cxn)
#	M2 = self.makeM2Widget(reactor, cxn)
#	M2pump = self.makeM2PumpWidget(reactor, cxn)
#
#	subtabWidget = QtGui.QTabWidget()
#
#	subtabWidget.addTab(wavemeter, '&Wavemeter')
#	subtabWidget.addTab(M2, '&M2')
#	subtabWidget.addTab(M2pump, '&PumpM2')
#
#       self.setCentralWidget(centralWidget)
#        self.setWindowTitle('Lasers')
#	return subtabWidget

######create widgets with shared connection######

    def makePulserWidget(self, reactor, cxn):
        from Qsim.clients.DDS.DDS_CONTROL import DDS_CONTROL
        DDS = DDS_CONTROL(reactor, cxn)
        return DDS

    def makeTsunamiWidget(self, reactor, cxn):
        from common.lib.clients.evPump.evPumpClient import eVPumpClient
        evpump = eVPumpClient(reactor)
        return evpump

    def makeScriptScannerWidget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        scriptscanner = script_scanner_gui(reactor, cxn = cxn)
        return scriptscanner

    def makeWavemeterWidget(self, reactor, cxn):
        from common.lib.clients.Multiplexer.multiplexerclient import wavemeterclient
        wavemeter = wavemeterclient(reactor, cxn)
        return wavemeter

    def makeM2Widget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from Qsim.clients.M2lasercontrol.M2laserControl import M2Window
        from Qsim.clients.M2pump.M2pumpclient import M2PumpClient
        gridLayout = QtGui.QGridLayout()
        pump = M2PumpClient(reactor, cxn)
        pump.setMaximumWidth(200)
        pump.setMinimumHeight(600)
        gridLayout.addWidget(M2Window(reactor, cxn),                  0,0,5,5)
        gridLayout.addWidget(pump,                0,5, 5,1)
        gridLayout.setSpacing(10)
        widget.setLayout(gridLayout)
        return widget

    def makeAnalysisWidget(self, reactor, cxn):
        from Qsim.clients.analysis.analysis import analysis
        analysis = analysis(reactor, cxn)
        return analysis

    def makeControlWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.lib.clients.PMT_Control.PMT_CONTROL import pmtWidget
        from Qsim.clients.kittykat.kittykatPulser import kittykatclient
        from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import switchclient
        from Qsim.clients.dac8718.dac8718client import dacclient

        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(dacclient(reactor, cxn),      0, 1, 4, 1)
        gridLayout.addWidget(kittykatclient(reactor, cxn), 3, 0, 1, 1)
        gridLayout.addWidget(pmtWidget(reactor, cxn),      1, 0, 1, 1)
        gridLayout.addWidget(cameraswitch(reactor, cxn),   0, 0, 1, 1)
        gridLayout.addWidget(switchclient(reactor, cxn),   2, 0, 1, 1)
        gridLayout.setSpacing(10)
        widget.setLayout(gridLayout)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( sys.argv )
    clipboard = a.clipboard()
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    QsimGUI = QSIM_GUI(reactor, clipboard)
    QsimGUI.setWindowIcon(QtGui.QIcon('/home/qsimexpcontrol/Pictures/icons/6ions.jpg'))
    QsimGUI.setWindowTitle('Qsim GUI')
    QsimGUI.show()
    reactor.run()
