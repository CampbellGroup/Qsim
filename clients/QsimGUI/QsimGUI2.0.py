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
	lasers = self.makeLaserSubTab(reactor, cxn)

	# add tabs
        self.tabWidget = QtGui.QTabWidget()

        self.tabWidget.addTab(script_scanner, '&Script Scanner')
	self.tabWidget.addTab(lasers, '&Lasers')
	

        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Qsim GUI')

#################### Here we will connect to individual clients and add sub-tabs #####################

    def makeLaserSubTab(self, reactor, cxn):
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout() 
	wavemeter = self.makeWavemeterWidget(reactor, cxn)
	M2 = self.makeM2Widget(reactor, cxn)
	subtabWidget = QtGui.QTabWidget()
	subtabWidget.addTab(wavemeter, '&Wavemeter')
	subtabWidget.addTab(M2, '&M2')
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Lasers')
	return subtabWidget
	
	

    def makeScriptScannerWidget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
	scriptscanner = script_scanner_gui(reactor, cxn = cxn)
        return scriptscanner

    def makeWavemeterWidget(self, reactor, cxn):
        from common.lib.clients.Multiplexer.multiplexerclient import wavemeterclient
	wavemeter = wavemeterclient(reactor, cxn)
        return wavemeter

    def makeM2Widget(self, reactor, cxn):
	from Qsim.clients.M2lasercontrol.M2laserControl import M2Window
	M2 = M2Window(reactor, cxn)
	return M2

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
