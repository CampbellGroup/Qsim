#!/usr/bin/python
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
        self.clipboard = clipboard
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.lib.clients.connection import connection
        cxn = connection(name='Qsim GUI Client')
        yield cxn.connect()
        self.create_layout(cxn)

    # Highest level adds tabs to big GUI
    def create_layout(self, cxn):
        #  creates central layout
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()

        #  create subwidgets to be added to tabs
        script_scanner = self.makeScriptScannerWidget(reactor, cxn)
        wavemeter = self.makeWavemeterWidget(reactor, cxn)
        control = self.makeControlWidget(reactor, cxn)
        # Pulser = self.makePulserWidget(reactor, cxn)
        # Config = self.makeConfigWidget(reactor, cxn)
        # Keithley = self.makeKeithleyWidget(reactor, cxn)
        evPump = self.makeEVPumpWidget(reactor, cxn)
        # WF = self.makeWindfreakWidget(reactor, cxn)

        # add tabs
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(wavemeter, '&Wavemeter')
        self.tabWidget.addTab(script_scanner, '&Script Scanner')
        self.tabWidget.addTab(control, '&Control')
        # self.tabWidget.addTab(Pulser, '&Pulser')
        # self.tabWidget.addTab(Config, '&Config')
        # self.tabWidget.addTab(Keithley, '&Keithleys')
        # self.tabWidget.addTab(PiezoBox, '&Piezo Box')
        self.tabWidget.addTab(evPump, '&EV Pump')
        # self.tabWidget.addTab(WF, '&Windfreak')

        self.tabWidget.setMovable(True)
        self.tabWidget.setCurrentIndex(2)

        layout.addWidget(self.tabWidget)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Qsim GUI')

    ###############################################################
    # Here we will connect to individual clients and add sub-tabs #
    ###############################################################

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
        pz_client = Piezo_Client(reactor)
        gridLayout.addWidget(pz_client)
        qwidget.setLayout(gridLayout)
        return qwidget

    def makeEVPumpWidget(self, reactor, cxn):
        from common.lib.clients.evPump.evPumpClient import eVPumpClient
        ev_widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(eVPumpClient(reactor, cxn=cxn))
        layout.addStretch()
        ev_widget.setLayout(layout)
        return ev_widget

    # def makeKeithleyWidget(self, reactor, cxn):
    #     qwidget = QtGui.QWidget()
    #     from Qsim.clients.keithley_control.keithley_controller import KeithleyClient as oven
    #     from common.lib.clients.keithley_2231A_30_3.keithley_2231A_30_3 import keithleyclient as b_field
    #     gridLayout = QtGui.QGridLayout()
    #     oven_keithley = oven(reactor, cxn)
    #     b_field_keithley = b_field(reactor, cxn)
    #     oven_keithley.setMaximumHeight(200)
    #     b_field_keithley.setMaximumHeight(400)
    #     gridLayout.addWidget(oven_keithley, 0, 0, 2, 0)
    #     gridLayout.addWidget(b_field_keithley, 1, 0, 2, 1)
    #     qwidget.setLayout(gridLayout)
    #     return qwidget

    def makeConfigWidget(self, reactor, cxn):
        from common.lib.clients.config_editor.config_editor import CONFIG_EDITOR
        widget = CONFIG_EDITOR(reactor, cxn)
        return widget

    def makeScriptScannerWidget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        scriptscanner = script_scanner_gui(reactor, cxn=cxn)
        return scriptscanner

    def makeWavemeterWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from common.lib.clients.Multiplexer.multiplexerclient import wavemeterclient
        # from Qsim.clients.single_wavemeter_channel.single_channel_wm import single_channel_wm
        # gridLayout = QtGui.QGridLayout()
        wavemeter = wavemeterclient(reactor, cxn)
        # ws7 = single_channel_wm(reactor)
        # gridLayout.addWidget(wavemeter)
        # gridLayout.addWidget(ws7)
        # wavemeter.setMaximumHeight(800)
        # widget.setLayout(gridLayout)
        # return widget
        return wavemeter

    def makeControlWidget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from Qsim.clients.RF_control.RFcontrol import RFcontrol
        from common.lib.clients.PMT_Control.PMT_CONTROL import pmtWidget
        from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import switchclient
        from Qsim.clients.dac_control.dac_client import dacclient
        from Qsim.clients.load_control.load_control import LoadControl
        from common.lib.clients.piezo_client.Piezo_Client import Piezo_Client
        from common.lib.clients.keithley_2231A_30_3.keithley_2231A_30_3 import keithleyclient

        from Qsim.clients.DDS.DDS_CONTROL import DDS_CONTROL
        from common.lib.clients.pulser_switch.pulser_switch_control import switchWidget
        from Qsim.clients.windfreak_client.windfreak_client import windfreak_client

        gridLayout = QtGui.QGridLayout()

        # addWidget(widget, vertical-pos, horizontal-pos, vertical-span, horizontal-span)
        # column one
        col_one_widget = QtGui.QWidget()
        col_one = QtGui.QVBoxLayout()
        col_one.addWidget(switchclient(reactor, cxn))
        col_one.addWidget(cameraswitch(reactor, cxn))
        col_one.addWidget(pmtWidget(reactor, cxn))
        col_one.addStretch(1)
        col_one.addWidget(RFcontrol(reactor, cxn))
        col_one_widget.setLayout(col_one)
        col_one_widget.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        gridLayout.addWidget(col_one_widget, 0, 0, 6, 1)

        gridLayout.addWidget(windfreak_client(reactor), 6, 0, 1, 3)

        # column two
        gridLayout.addWidget(dacclient(reactor, cxn), 0, 1, 4, 2)
        gridLayout.addWidget(LoadControl(reactor), 4, 1, 2, 1)
        gridLayout.addWidget(Piezo_Client(reactor), 4, 2, 2, 1)
        # column three

        col_three_widget = QtGui.QWidget()
        col_three = QtGui.QVBoxLayout()
        col_three.addWidget(DDS_CONTROL(reactor, cxn))
        col_three.addWidget(switchWidget(reactor))
        col_three.addWidget(keithleyclient(reactor, cxn))
        col_three.addStretch(1)
        col_three_widget.setLayout(col_three)
        gridLayout.addWidget(col_three_widget, 0, 3, 8, 2)

        # gridLayout.setSpacing(1)
        widget.setLayout(gridLayout)
        return widget
    #
    # def makeWindfreakWidget(self, reactor, cxn):
    #     from Qsim.clients.windfreak_client.windfreak_client import windfreak_client
    #     wf_client = windfreak_client(reactor)
    #     return wf_client

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
