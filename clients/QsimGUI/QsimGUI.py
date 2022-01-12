#!/usr/bin/python
import os
import sys

from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks
from Qsim.clients.qtui.detachable_tab import DetachableTabWidget

sys.path.append('/home/qsimexpcontrol/LabRAD/')
sys.path.append('/home/qsimexpcontrol/LabRAD/Qsim')
os.environ["LABRADPASSWORD"] = "lab"

class QSIM_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, clipboard, parent=None):
        super(QSIM_GUI, self).__init__(parent)
        self.clipboard = clipboard
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
        control = self.makeControlWidget(reactor, cxn)
       # Ultrafast = self.makeUltrafastWidget(reactor, cxn)
        Pulser = self.makePulserWidget(reactor, cxn)
        Config = self.makeConfigWidget(reactor, cxn)
        #Keithley = self.makeKeithleyWidget(reactor, cxn)
        PiezoBox = self.makePiezoWidget(reactor, cxn)
        WF = self.makeWindfreakWidget(reactor, cxn)

        # add tabs
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(wavemeter, '&Wavemeter')
        self.tabWidget.addTab(script_scanner, '&Script Scanner')
        self.tabWidget.addTab(control, '&Control')
        self.tabWidget.addTab(Pulser, '&Pulser')
        self.tabWidget.addTab(Config, '&Config')
        #self.tabWidget.addTab(Ultrafast, '&Ultrafast')
        #self.tabWidget.addTab(Keithley, '&Keithleys')
        self.tabWidget.addTab(PiezoBox, '&Piezo Box')
        self.tabWidget.addTab(WF, '&Windfreak')
        self.tabWidget.setMovable(True)

        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Qsim GUI')

#################### Here we will connect to individual clients and add sub-tabs #####################

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

    def makePiezoWidget(self, reactor, cxn):
        qwidget = QtGui.QWidget()
        from common.lib.clients.piezo_client.Piezo_Client import Piezo_Client
        gridLayout = QtGui.QGridLayout()
        pzclient = Piezo_Client(reactor)
        gridLayout.addWidget(pzclient)
        qwidget.setLayout(gridLayout)
        return qwidget

    # def makeKeithleyWidget(self, reactor, cxn):
    #     qwidget = QtGui.QWidget()
    #     from Qsim.clients.kiethley_control.kiethley_controller import kiethleyclient as oven
    #     from common.lib.clients.keithley_2231A_30_3.keithley_2231A_30_3 import kiethleyclient as bfield
    #     gridLayout = QtGui.QGridLayout()
    #     ovenKiethley = oven(reactor, cxn)
    #     bfieldKiethley = bfield(reactor, cxn)
    #     ovenKiethley.setMaximumHeight(200)
    #     bfieldKiethley.setMaximumHeight(400)
    #     gridLayout.addWidget(ovenKiethley, 0, 0, 2, 0)
    #     gridLayout.addWidget(bfieldKiethley, 1, 0, 2, 1)
    #     qwidget.setLayout(gridLayout)
    #     return qwidget

    def makeConfigWidget(self, reactor, cxn):
        from common.lib.clients.config_editor.config_editor import CONFIG_EDITOR
        widget = CONFIG_EDITOR(reactor, cxn)
        return widget

    # def makeUltrafastWidget(self, reactor, cxn):
    #     twidget = QtGui.QWidget()
    #     from common.lib.clients.evPump.evPumpClient import eVPumpClient
    #     from common.lib.clients.bristol.bristol_client import bristol_client
    #     #from Qsim.clients.time_harp_client.time_harp_client import TimeHarpClient
    #     gridLayout = QtGui.QGridLayout()
    #     evpump = eVPumpClient(reactor)
    #     evpump.setMaximumHeight(500)
    #     bristol = bristol_client(reactor)
    #     #timeharp = TimeHarpClient(reactor, cxn)
    #     #timeharp.setMaximumHeight(620)
    #     bristol.setMaximumHeight(200)
    #     gridLayout.addWidget(evpump, 0, 0)
    #     gridLayout.addWidget(bristol, 1, 0, 1, 2)
    #     #gridLayout.addWidget(timeharp, 0, 1)
    #     twidget.setLayout(gridLayout)
    #     return twidget

    def makeScriptScannerWidget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        scriptscanner = script_scanner_gui(reactor, cxn=cxn)
        return scriptscanner

    def makeWavemeterWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.lib.clients.Multiplexer.multiplexerclient import wavemeterclient
        from Qsim.clients.single_wavemeter_channel.single_channel_wm import single_channel_wm
        gridLayout = QtGui.QGridLayout()
        wavemeter = wavemeterclient(reactor, cxn)
        ws7 = single_channel_wm(reactor)
        gridLayout.addWidget(wavemeter)
        gridLayout.addWidget(ws7)
        wavemeter.setMaximumHeight(800)
        widget.setLayout(gridLayout)
        return widget

    def makeControlWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from Qsim.clients.RF_control.RFcontrol import RFcontrol
        from common.lib.clients.PMT_Control.PMT_CONTROL import pmtWidget
        from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import switchclient
        from Qsim.clients.dac_control.dac_client import dacclient
        from Qsim.clients.load_control.load_control import LoadControl
#        from Qsim.clients.load_indicator.load_indicator import LoadIndicator

        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(pmtWidget(reactor, cxn),      1, 0, 1, 1)
        gridLayout.addWidget(RFcontrol(reactor, cxn),      3, 0, 1, 1)
        gridLayout.addWidget(cameraswitch(reactor, cxn),   2, 0, 1, 1)
        gridLayout.addWidget(switchclient(reactor, cxn),   0, 0, 1, 1)
        gridLayout.addWidget(dacclient(reactor, cxn),      0, 1, 2, 1)
        gridLayout.addWidget(LoadControl(reactor),         2, 1, 2, 1)
#        gridLayout.addWidget(LoadIndicator(reactor),       3, 1, 2, 1)
        gridLayout.setSpacing(1)
        widget.setLayout(gridLayout)
        return widget

    def makeWindfreakWidget(self, reactor, cxn):
        from Qsim.clients.windfreak_client.windfreak_client import windfreak_client
        wfclient = windfreak_client(reactor)
        return wfclient

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    clipboard = a.clipboard()
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    QsimGUI = QSIM_GUI(reactor, clipboard)
    QsimGUI.setWindowIcon(QtGui.QIcon('/home/qsimexpcontrol/Pictures/icons/6ions.jpg'))
    QsimGUI.setWindowTitle('Qsim GUI')
    QsimGUI.show()
    reactor.run()
