#!/usr/bin/python
import os
import sys

from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks

sys.path.append('/home/qsimexpcontrol/LabRAD/')
sys.path.append('/home/qsimexpcontrol/LabRAD/Qsim')
os.environ["LABRADPASSWORD"] = "lab"


class QsimGUI(QtGui.QMainWindow):
    def __init__(self, reactor, clipboard, parent=None):
        super(QsimGUI, self).__init__(parent)
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
        central_widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()

        #  create subwidgets to be added to tabs
        script_scanner = self.make_script_scanner_widget(reactor, cxn)
        wavemeter = self.make_wavemeter_widget(reactor, cxn)
        control = self.make_control_widget(reactor, cxn)
        # Pulser = self.makePulserWidget(reactor, cxn)
        # Config = self.makeConfigWidget(reactor, cxn)
        # Keithley = self.makeKeithleyWidget(reactor, cxn)
        ev_pump = self.make_ev_pump_widget(reactor, cxn)
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
        self.tabWidget.addTab(ev_pump, '&EV Pump')
        # self.tabWidget.addTab(WF, '&Windfreak')

        self.tabWidget.setMovable(True)
        self.tabWidget.setCurrentIndex(2)

        layout.addWidget(self.tabWidget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Qsim GUI')

    ###############################################################
    # Here we will connect to individual clients and add sub-tabs #
    ###############################################################

    def make_pulser_widget(self, reactor, cxn):
        from Qsim.clients.DDS.dds_control import DDSControlWidget
        from common.lib.clients.pulser_switch.pulser_switch_control import switchWidget
        puls_widget = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()

        dds = DDSControlWidget(reactor, cxn)
        switch = switchWidget(reactor)
        grid_layout.addWidget(dds)
        grid_layout.addWidget(switch)
        puls_widget.setLayout(grid_layout)
        return puls_widget

    def make_piezo_widget(self, reactor, cxn):
        qwidget = QtGui.QWidget()
        from common.lib.clients.piezo_client.Piezo_Client import Piezo_Client
        grid_layout = QtGui.QGridLayout()
        pz_client = Piezo_Client(reactor)
        grid_layout.addWidget(pz_client)
        qwidget.setLayout(grid_layout)
        return qwidget

    def make_ev_pump_widget(self, reactor, cxn):
        from common.lib.clients.evPump.evPumpClient import eVPumpClient
        ev_widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(eVPumpClient(reactor, cxn=cxn))
        layout.addStretch()
        ev_widget.setLayout(layout)
        return ev_widget

    def make_keithley_widget(self, reactor, cxn):
        qwidget = QtGui.QWidget()
        from Qsim.clients.keithley_control.keithley_controller import KeithleyClient as Oven
        from common.lib.clients.keithley_2231A_30_3.keithley_2231A_30_3 import keithleyclient as b_field
        grid_layout = QtGui.QGridLayout()
        oven_keithley = Oven(reactor, cxn)
        b_field_keithley = b_field(reactor, cxn)
        oven_keithley.setMaximumHeight(200)
        b_field_keithley.setMaximumHeight(400)
        grid_layout.addWidget(oven_keithley, 0, 0, 2, 0)
        grid_layout.addWidget(b_field_keithley, 1, 0, 2, 1)
        qwidget.setLayout(grid_layout)
        return qwidget

    def make_config_widget(self, reactor, cxn):
        from common.lib.clients.config_editor.config_editor import CONFIG_EDITOR
        widget = CONFIG_EDITOR(reactor, cxn)
        return widget

    def make_script_scanner_widget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import ScriptScannerGui
        scriptscanner = ScriptScannerGui(reactor, cxn=cxn)
        return scriptscanner

    def make_wavemeter_widget(self, reactor, cxn):
        # widget = QtGui.QWidget()
        from common.lib.clients.Multiplexer.multiplexerclient import WavemeterClient
        # from Qsim.clients.single_wavemeter_channel.single_channel_wm import single_channel_wm
        # gridLayout = QtGui.QGridLayout()
        wavemeter = WavemeterClient(reactor, cxn)
        # ws7 = single_channel_wm(reactor)
        # gridLayout.addWidget(wavemeter)
        # gridLayout.addWidget(ws7)
        # wavemeter.setMaximumHeight(800)
        # widget.setLayout(gridLayout)
        # return widget
        return wavemeter

    def make_control_widget(self, reactor, cxn):
        widget = QtGui.QWidget()
        from Qsim.clients.RF_control.RFcontrol import RFcontrol
        from common.lib.clients.PMT_Control.PMT_CONTROL import pmtWidget
        from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import switchclient
        from Qsim.clients.dac_control.dac_client import dacclient
        from Qsim.clients.load_control.load_control import LoadControl
        from common.lib.clients.piezo_client.Piezo_Client import Piezo_Client
        from common.lib.clients.keithley_2231A_30_3.keithley_2231A_30_3 import keithleyclient

        from Qsim.clients.DDS.dds_control import DDSControlWidget
        from common.lib.clients.pulser_switch.pulser_switch_control import switchWidget
        from Qsim.clients.windfreak_client.windfreak_client import windfreak_client

        grid_layout = QtGui.QGridLayout()

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
        grid_layout.addWidget(col_one_widget, 0, 0, 6, 1)

        grid_layout.addWidget(windfreak_client(reactor), 6, 0, 1, 3)

        # column two
        grid_layout.addWidget(dacclient(reactor, cxn), 0, 1, 4, 2)
        grid_layout.addWidget(LoadControl(reactor), 4, 1, 2, 1)
        grid_layout.addWidget(Piezo_Client(reactor), 4, 2, 2, 1)
        # column three

        col_three_widget = QtGui.QWidget()
        col_three = QtGui.QVBoxLayout()
        col_three.addWidget(DDSControlWidget(reactor, cxn))
        col_three.addWidget(switchWidget(reactor))
        col_three.addWidget(keithleyclient(reactor, cxn))
        col_three.addStretch(1)
        col_three_widget.setLayout(col_three)
        grid_layout.addWidget(col_three_widget, 0, 3, 8, 2)

        # grid_layout.setSpacing(1)
        widget.setLayout(grid_layout)
        return widget

    def make_windfreak_widget(self, reactor, cxn):
        from Qsim.clients.windfreak_client.windfreak_client import windfreak_client
        wf_client = windfreak_client(reactor)
        return wf_client

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    clipboard = a.clipboard()
    import qt4reactor

    qt4reactor.install()
    from twisted.internet import reactor

    gui = QsimGUI(reactor, clipboard)
    gui.setWindowIcon(QtGui.QIcon('/home/qsimexpcontrol/Pictures/icons/6ions.jpg'))
    gui.setWindowTitle('Qsim GUI')
    gui.show()
    reactor.run()
