#!/usr/bin/env python
import os
import sys

from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks

sys.path.append('/home/qsimexpcontrol/LabRAD/')
sys.path.append('/home/qsimexpcontrol/LabRAD/Qsim')
os.environ["LABRADPASSWORD"] = "lab"

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
        #  creates central layout
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()

        #  create subwidgets to be added to tabs
        script_scanner = self.makeScriptScannerWidget(reactor, cxn)
        wavemeter = self.makeWavemeterWidget(reactor, cxn)
        #M2 = self.makeM2Widget(reactor, cxn)
        control = self.makeControlWidget(reactor, cxn)
        analysis = self.makeAnalysisWidget(reactor, cxn)
        Tsunami = self.makeTsunamiWidget(reactor, cxn)
        Pulser = self.makePulserWidget(reactor, cxn)
        Config = self.makeConfigWidget(reactor, cxn)
#        Histogram = self.makeHistogramWidget(reactor, cxn)
        Keithley = self.makeKeithleyWidget(reactor, cxn)
        

        # add tabs
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(wavemeter, '&Wavemeter')
        self.tabWidget.addTab(script_scanner, '&Script Scanner')
        self.tabWidget.addTab(control, '&Control')
        self.tabWidget.addTab(Pulser, '&Pulser')
#        self.tabWidget.addTab(Histogram, '&Histogram')
        self.tabWidget.addTab(analysis, '&Analysis')
        self.tabWidget.addTab(Config, '&Config')
        self.tabWidget.addTab(Tsunami, '&Tsunami')
        self.tabWidget.addTab(Keithley, '&Keithley')
        self.tabWidget.setMovable(True)


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
        from common.lib.clients.pulser_switch.pulser_switch_control import switchWidget
        puls_widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()

        DDS = DDS_CONTROL(reactor, cxn)
        switch = switchWidget(reactor)
        gridLayout.addWidget(DDS)
        gridLayout.addWidget(switch)
        puls_widget.setLayout(gridLayout)
        return puls_widget

#    def makeRigolWidget(self, reactor, cxn):
#        from clients.kiethley_control.rigolcontroller_usbtmc import rigolclient
#        widget = rigolclient(reactor, cxn)
#        return widget

    def makeKeithleyWidget(self, reactor, cxn):
        from Qsim.clients.kiethley_control.kiethley_controller import kiethleyclient
        widget = kiethleyclient(reactor, cxn)
        return widget


    def makeConfigWidget(self, reactor, cxn):
        from common.lib.clients.config_editor.config_editor import CONFIG_EDITOR
        widget = CONFIG_EDITOR(reactor, cxn)
        return widget

    def makeTsunamiWidget(self, reactor, cxn):
        twidget = QtGui.QWidget()
        from common.lib.clients.evPump.evPumpClient import eVPumpClient
        from common.lib.clients.bristol.bristol_client import bristol_client
        gridLayout = QtGui.QGridLayout()
        evpump = eVPumpClient(reactor)
        evpump.setMinimumHeight(700)
        bristol = bristol_client(reactor)
        gridLayout.addWidget(evpump)
        gridLayout.addWidget(bristol)
        twidget.setLayout(gridLayout)
        return twidget

    def makeScriptScannerWidget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        scriptscanner = script_scanner_gui(reactor, cxn = cxn)
        return scriptscanner

    def makeWavemeterWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.lib.clients.Multiplexer.multiplexerclient import wavemeterclient
        from Qsim.clients.single_wavemeter_channel.single_channel_wm import single_channel_wm
        from Qsim.clients.WM_DAC_Control.wm_dac_control import wm_dac_control
        gridLayout = QtGui.QGridLayout()
        wavemeter = wavemeterclient(reactor, cxn)
        ws7 = single_channel_wm(reactor)
        dac_control = wm_dac_control(reactor)
        gridLayout.addWidget(wavemeter)
        gridLayout.addWidget(dac_control)
        gridLayout.addWidget(ws7)
        wavemeter.setMaximumHeight(820)
        widget.setLayout(gridLayout)
        return widget

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
        from Qsim.clients.RF_control.RFcontrol import RFcontrol
        from common.lib.clients.PMT_Control.PMT_CONTROL import pmtWidget
        from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import switchclient
        from Qsim.clients.dac_control.dac_client import dacclient
        from Qsim.clients.load_control.load_control import LoadControl

        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(pmtWidget(reactor, cxn),      1, 0, 1, 1)
        gridLayout.addWidget(RFcontrol(reactor, cxn),      3, 0, 1, 1)
        gridLayout.addWidget(cameraswitch(reactor, cxn),   2, 0, 1, 1)
        gridLayout.addWidget(switchclient(reactor, cxn),   0, 0, 1, 1)
        gridLayout.addWidget(dacclient(reactor, cxn),      0, 1, 2, 1)
        gridLayout.addWidget(LoadControl(reactor, cxn),    2, 1, 2, 1)
        gridLayout.setSpacing(10)
        widget.setLayout(gridLayout)
        return widget

#    def makeHistogramWidget(self, reactor, cxn):
#        from barium.lib.clients.Histogram_client.readout_histogram import readout_histogram
#        hist = readout_histogram(reactor, cxn)
#        return hist

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
